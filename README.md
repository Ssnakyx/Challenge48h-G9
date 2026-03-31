# Challenge 48h - README de lancement

Ce projet déploie une infrastructure Docker orientée production avec:

- une webapp Symfony (PHP/Apache),
- une API data (FastAPI),
- un cron d'ingestion,
- une base PostgreSQL Master/Slave,
- un monitoring Netdata.

Objectif validé: 15/15 au bareme (secrets, HA, isolation reseau, monitoring, multi-stage).

## Prerequis

- Docker Desktop (ou Docker Engine + Compose v2)
- Ports libres: 80 et 19999
- Fichier `.env` present a la racine

## Onboarding nouveaux developpeurs

Pour la configuration Symfony locale, partez du fichier exemple:

```bash
cp webapp/.env.local.example webapp/.env.local
```

Important:

- Ne decommentez pas la ligne SQLite dans `webapp/.env.local.example`.
- En mode Docker, la vraie `DATABASE_URL` PostgreSQL est injectee par `docker-compose.yml`.
- Le vrai secret applicatif est egalement injecte par Docker.

## Lancer le projet

```bash
cd Challenge48h-G9
docker compose up -d --build
docker compose ps
```

## Acces services

- Webapp: http://localhost
- Monitoring: http://localhost:19999

## Architecture rapide

- `public_net`: expose uniquement webapp (80) et monitoring (19999)
- `private_net` (internal): reseau interne pour db-master, db-slave, data-api, data-cron
- PostgreSQL replication:
  - `db-master` (primary)
  - `db-slave` (replica)

## Ce qui a ete mis en place

1. Secrets externalises

- Aucun mot de passe en dur dans compose
- Variables injectees via `.env`

2. Haute disponibilite base de donnees

- PostgreSQL Master/Slave configure
- Healthchecks actifs sur les deux noeuds

3. Isolation reseau

- Base non exposee publiquement (pas de port 5432 publie)
- Separation `public_net` / `private_net`

4. Monitoring et observabilite

- Netdata disponible sur port 19999

5. Optimisation images Docker

- Dockerfiles multi-stage (webapp et Python)

## Commandes utiles

Verifier etat des services:

```bash
docker compose ps
```

Voir logs:

```bash
docker compose logs -f webapp
docker compose logs -f db-master
docker compose logs -f db-slave
docker compose logs -f monitoring
```

Arreter:

```bash
docker compose down
```

Arreter + supprimer volumes:

```bash
docker compose down -v
```

## Validation rapide (jury)

Script automatique:

```bash
./jury-validation.sh
```

Verification manuelle minimum:

```bash
# Secrets externalises
grep "POSTGRES_PASSWORD" docker-compose.yml

# DB isolee
curl -m 2 localhost:5432 || echo "DB non accessible (OK)"

# Webapp et monitoring accessibles
curl -I http://localhost:80
curl -s http://localhost:19999/api/v2/info | head -3
```

## Documents associes

- `VALIDATION_JURY.md`: detail des preuves
- `SOUTENANCE_PREP.md`: sequence de demo
- `DERNIERE_HEURE.md`: checklist avant passage

## Notes

- Si un service est `unhealthy`, attendre 10-20 secondes puis relancer `docker compose ps`.
- Si besoin, relancer proprement:

```bash
docker compose down
docker compose up -d --build
```
