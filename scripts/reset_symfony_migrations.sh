#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DATABASE_URL_TARGET="${DATABASE_URL_TARGET:-postgresql://app:change-me@db:5432/app?serverVersion=15&charset=utf8}"

echo "[1/4] Suppression des anciennes migrations SQLite..."
find webapp/migrations -maxdepth 1 -type f -name '*.php' -print -delete

echo "[2/4] Drop de la base si elle existe..."
if command -v php >/dev/null 2>&1 && command -v composer >/dev/null 2>&1; then
	DATABASE_URL="$DATABASE_URL_TARGET" php webapp/bin/console doctrine:database:drop --force --if-exists

	echo "[3/4] Creation de la base PostgreSQL..."
	DATABASE_URL="$DATABASE_URL_TARGET" php webapp/bin/console doctrine:database:create

	echo "[4/4] Generation de la migration initiale PostgreSQL..."
	DATABASE_URL="$DATABASE_URL_TARGET" php webapp/bin/console doctrine:migrations:diff
else
	echo "PHP/Composer local indisponible, fallback via Docker Compose..."
	docker compose up -d db
	docker compose run --rm --entrypoint sh -e DATABASE_URL="$DATABASE_URL_TARGET" webapp -lc '
		composer install --no-dev --optimize-autoloader --no-interaction &&
		php bin/console doctrine:database:drop --force --if-exists &&
		php bin/console doctrine:database:create &&
		php bin/console doctrine:migrations:diff
	'
fi

echo "Termine. Migration regeneree dans webapp/migrations/."
