# Challenge 48h – Indice météo / pollution

Ce repo propose un pipeline de données et une API en Python/FastAPI qui :

- télécharge les mesures horaires de polluants (flux E2) ainsi que les métadonnées stations publiées sur data.gouv.fr ;
- récupère les observations météo SYNOP (Météo France) sur la même période ;
- effectue une jointure spatio-temporelle station par station via une recherche du voisin météo le plus proche (BallTree en coordonnées Haversine) ;
- calcule un indice composite (pollution + conditions météo) avec pondération configurable et catégorisation (low/moderate/high/critical) ;
- stocke le résultat + les prévisions linéaires dans une base SQLite ;
- expose les données aux devs via une API FastAPI (`/health`, `/indices`, `/stations/{code}/indices`, `/forecasts`).

## Structure

```
app/
  config.py          # lecture des variables d'env et chemins par défaut
  constants.py       # seuils réglementaires, poids de l'indice, etc.
  data_clients.py    # téléchargement des fichiers data.gouv.fr
  data_pipeline.py   # orchestration : ingestion -> processing -> persistance
  db.py              # création du moteur SQLAlchemy
  forecasting.py     # régression linéaire simple pour la prévision
  main.py            # API FastAPI
  models.py          # tables SQLite (stations, indices, prévisions)
  processors.py      # nettoyage pandas + jointure géospatiale + scoring
  schemas.py         # schémas Pydantic renvoyés par l'API
```

`data/` contient de petits CSV d'exemple qui servent de fallback lorsque les téléchargements externes sont indisponibles.

## Pré-requis

- Python 3.11+

## Configuration

Copier le fichier `.env.example` :

```bash
cp .env.example .env
# Adapter les URLs, la fenêtre temporelle par défaut, etc.
```

Variables importantes :

- `DATABASE_URL` : connexion SQLAlchemy (par défaut `sqlite:///data/air_quality.db`).
- `POLLUTION_BUCKET` / `POLLUTION_PREFIX` : bucket S3 data.gouv à lister.
- `POLLUTION_METADATA_URL` : XLS "Dataset D" pour récupérer les coordonnées des stations.
- `WEATHER_RESOURCE_URL` : archive `synop_YYYY.csv.gz` (choisir l'année qui couvre la fenêtre visée, ex. `synop_2026.csv.gz` pour des données temps réel).
- `DEFAULT_START_DATE` / `DEFAULT_END_DATE` : fenêtre temporelle (UTC) utilisée quand on n'indique rien à la CLI.
- `MAX_DISTANCE_KM` : rayon maximal pour associer une station météo à une station pollution.
- `FORECAST_HORIZON_HOURS` : horizon de prévision linéaire.
- `REALTIME_WINDOW_HOURS` : taille de la fenêtre glissante (en heures) utilisée quand on récupère les dernières données temps réel.

## Installation locale

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

La base SQLite (`data/air_quality.db`) est créée automatiquement lors de la première exécution.

Lancer un run d'ingestion (fenêtre passée) :

```bash
python -m app.data_pipeline --start-date 2024-01-01 --end-date 2024-01-03
```

Cela :
1. télécharge quelques jours de données (max 7 fichiers CSV jour par jour pour limiter le volume) ;
2. joint pollution + météo ;
3. calcule l'indice ;
4. alimente les tables `stations`, `impact_indices`, `impact_forecasts`.

Mode temps réel : sans date (ou avec `--realtime`) la pipeline télécharge automatiquement les derniers fichiers publiés et filtre sur la fenêtre définie par `REALTIME_WINDOW_HOURS` :

```bash
python -m app.data_pipeline --realtime --window-hours 12  # ex : dernières 12 h
```

Ensuite démarrer l'API :

```bash
uvicorn app.main:app --reload
# Swagger: http://localhost:8000/docs
```

## Endpoints principaux

- `GET /health` : statut + nombre d'indices/prévisions stockés.
- `GET /indices?station_code=FR01005&limit=24` : derniers indices calculés (filtrable par niveau d'impact).
- `GET /stations/{code}/indices` : historique pour une station donnée.
- `GET /forecasts?station_code=FR01005` : prévisions issues de la régression linéaire simple.

## Calcul de l'indice

1. Chaque mesure horaire est normalisée via les seuils réglementaires (`constants.POLLUTANT_THRESHOLDS`).
2. La somme pondérée (`constants.POLLUTANT_WEIGHTS`) donne un score pollution par station/heure.
3. Les conditions météo (température, humidité, vent, pluie) modulent le risque via `WEATHER_WEIGHTS` (vent/pluie réduisent l'impact car elles dispersent / lavent les polluants).
4. L'indice final est borné à `[0, 100]` et catégorisé : `low`, `moderate`, `high`, `critical`.
5. Bonus : pour chaque station on entraîne une régression linéaire simple `indice = a * temps + b` pour projeter `N` heures dans le futur.

Tous les paramètres (poids, seuils, rayon géographique, horizon de prévision) peuvent être ajustés dans `constants.py` ou via l'environnement. Le fichier SQLite peut être inspecté avec `sqlite3 data/air_quality.db ".tables"` une fois la pipeline exécutée.

## Tests rapides sans réseau

Les CSV de `data/sample_*.csv` permettent de lancer la pipeline hors-ligne. Il suffit de supprimer/renommer votre `.env` (ou de forcer des dates où le téléchargement échoue) pour que le client tombe automatiquement sur ces jeux d'exemple.

## Aller plus loin

- Ajouter une étape dbt / marts pour historiser plus finement chaque polluant.
- Connecter un scheduler (Dagster, Airflow) pour automatiser l'ingestion horaire.
- Exposer un endpoint `/refresh` sécurisé pour déclencher l'ingestion à la demande.
- Remplacer la régression linéaire par un modèle multivarié (RandomForest, Prophet) si nécessaire.
