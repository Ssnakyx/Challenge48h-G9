"""
Shared constants for the pollution/weather impact pipeline.
"""

from __future__ import annotations

from typing import Final, List

# Conversion constants
EARTH_RADIUS_KM: Final[float] = 6371.0

# Regulatory thresholds used to normalize pollutant concentrations (µg/m³).
POLLUTANT_THRESHOLDS: Final[dict[str, float]] = {
    "PM10": 50.0,
    "PM2.5": 25.0,
    "NO2": 200.0,
    "SO2": 350.0,
    "O3": 180.0,
    "CO": 10000.0,
}

# Derived helper thresholds (low / medium / alert) used for custom alerting logic.
POLLUTANT_LEVEL_THRESHOLDS: Final[dict[str, dict[str, float]]] = {
    pollutant: {
        "low": threshold * 0.4,
        "medium": threshold * 0.7,
        "alert": threshold,
    }
    for pollutant, threshold in POLLUTANT_THRESHOLDS.items()
}

# Weight assigned to each pollutant when building the composite score.
POLLUTANT_WEIGHTS: Final[dict[str, float]] = {
    "PM10": 0.22,
    "PM2.5": 0.28,
    "NO2": 0.18,
    "SO2": 0.08,
    "O3": 0.18,
    "CO": 0.06,
}

# Weather contribution weights. Positive values increase the risk,
# negative values mitigate the pollution effect.
WEATHER_WEIGHTS: Final[dict[str, float]] = {
    "temperature": 0.35,
    "humidity": 0.35,
    "wind": -0.2,
    "precipitation": -0.1,
}

# Default column names that we look for when parsing source files.
POLLUTION_COLUMNS: Final[dict[str, str]] = {
    "date_debut": "period_start",
    "date_de_debut": "period_start",
    "date_de_fin": "period_end",
    "date_fin": "period_end",
    "code_site": "station_code",
    "nom_site": "station_name",
    "polluant": "pollutant",
    "valeur": "value",
    "valeur_brute": "raw_value",
    "unite_de_mesure": "unit",
    "unite_mesure": "unit",
}

METADATA_LATITUDE_KEYS: Final[List[str]] = [
    "latitude",
    "latitude_wgs84",
    "lat",
]
METADATA_LONGITUDE_KEYS: Final[List[str]] = [
    "longitude",
    "longitude_wgs84",
    "lon",
]
