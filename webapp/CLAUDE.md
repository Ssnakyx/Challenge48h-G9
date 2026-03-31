# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AirMetrics is a Symfony 8 web application for visualizing air quality and weather data on an interactive map. It displays pollution measurements (PM10, PM2.5, NO2, SO2, O3, CO) and weather data from geographic monitoring stations using Leaflet maps.

## Common Commands

```bash
# Install PHP dependencies
composer install

# Install JS assets (importmap)
php bin/console importmap:install

# Start dev server
symfony serve

# Start full stack with Docker (PostgreSQL + Mailpit)
docker compose up -d

# Database migrations
php bin/console doctrine:migrations:migrate
php bin/console make:migration        # generate from entity changes

# Load fixtures (test data)
php bin/console doctrine:fixtures:load

# Run tests
vendor/bin/phpunit
vendor/bin/phpunit tests/SomeTest.php  # single test file

# Debug routes
php bin/console debug:router

# Clear cache
php bin/console cache:clear
```

## Architecture

### Data Model

Three core entities with a hub-and-spoke relationship:
- **GeoPoint** — monitoring station (code, name, lat/lon, timestamp)
- **PollutionMeasurements** → GeoPoint — per-pollutant value+score columns plus overall score
- **WeatherMeasurements** → GeoPoint — temperature, humidity, wind, pressure + score

### Controllers & Routing

Routes are defined via PHP `#[Route]` attributes, auto-discovered from `src/Controller/`.

- `HomeController` (`/`) — renders home page with Leaflet map centered on Lyon
- `MapController` (`/map`) — invokable controller with enhanced map + info windows

### Frontend

- **Twig templates** are component-based using `{% include %}` partials in `templates/home/`
- **Stimulus.js** controllers live in `assets/controllers/` (attribute-driven JS)
- **Symfony UX Leaflet** (`ux_map`) handles map rendering — configured in `config/packages/ux_map.yaml` with `leaflet://default` DSN
- **Asset Mapper** (not Webpack) handles JS bundling via `importmap.php`
- Heavy CSS (animations, aurora effects) lives inline in `templates/home/_styles.html.twig`

### Key Config

- `.env` — base config; override locally with `.env.local`
- Database: PostgreSQL 16 via Docker (`compose.yaml`), connection in `DATABASE_URL`
- Mailpit available at `http://localhost:8025` for email testing in dev
- Map DSN: `UX_MAP_DSN=leaflet://default`

### Forms

`MapFilterType` + `MapFilterData` DTO provide date-based filtering for map data. The form system uses Symfony's `DateTimeType` with standard data binding.
