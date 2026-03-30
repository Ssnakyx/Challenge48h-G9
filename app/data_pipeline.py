"""
Command line entry point that drives ingestion, processing and persistence.
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from .config import get_settings
from .data_clients import DataGouvClient
from .db import SessionLocal, engine
from .models import Base, GeoPoint, PollutionMeasurement, WeatherMeasurement
from .processors import (
    aggregate_pollution,
    attach_station_metadata,
    match_and_score,
    prepare_pollution_dataframe,
    prepare_weather_dataframe,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

POLLUTANT_COLUMN_MAP = {
    "PM10": ("pm10_value", "pm10_score"),
    "PM2.5": ("pm25_value", "pm25_score"),
    "NO2": ("no2_value", "no2_score"),
    "SO2": ("so2_value", "so2_score"),
    "O3": ("o3_value", "o3_score"),
    "CO": ("co_value", "co_score"),
}
POLLUTANT_FIELDS = {field for pair in POLLUTANT_COLUMN_MAP.values() for field in pair}

def _parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return pd.to_datetime(value, utc=True).to_pydatetime()


def _ensure_utc_timestamp(value) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tz is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def _safe_float(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if pd.isna(value):
        return None
    return float(value)


def _apply_pollutant_columns(pollution_obj, payload: list) -> None:
    for field in POLLUTANT_FIELDS:
        setattr(pollution_obj, field, None)
    for entry in payload or []:
        pollutant = (entry.get("pollutant") or "").upper()
        mapping = POLLUTANT_COLUMN_MAP.get(pollutant)
        if not mapping:
            continue
        value_col, score_col = mapping
        setattr(pollution_obj, value_col, _safe_float(entry.get("value")))
        setattr(pollution_obj, score_col, _safe_float(entry.get("score")))


def _get_or_create_geo_point(session, row: pd.Series) -> GeoPoint:
    timestamp = pd.to_datetime(row["timestamp"], utc=True).to_pydatetime()
    station_code = row.get("station_code")
    geo_point = (
        session.query(GeoPoint)
        .filter(
            GeoPoint.station_code == station_code,
            GeoPoint.timestamp == timestamp,
        )
        .one_or_none()
    )
    if geo_point:
        updated = False
        lat = _safe_float(row.get("latitude"))
        lon = _safe_float(row.get("longitude"))
        name = row.get("station_name")
        if lat is not None and geo_point.latitude != lat:
            geo_point.latitude = lat
            updated = True
        if lon is not None and geo_point.longitude != lon:
            geo_point.longitude = lon
            updated = True
        if name and geo_point.station_name != name:
            geo_point.station_name = name
            updated = True
        if updated:
            session.add(geo_point)
        return geo_point

    geo_point = GeoPoint(
        station_code=station_code,
        station_name=row.get("station_name"),
        latitude=_safe_float(row.get("latitude")),
        longitude=_safe_float(row.get("longitude")),
        timestamp=timestamp,
        date=timestamp.date(),
    )
    session.add(geo_point)
    session.flush()
    return geo_point


def _persist_measurements(session, df: pd.DataFrame) -> None:
    inserted = 0
    for _, row in df.iterrows():
        geo_point = _get_or_create_geo_point(session, row)
        timestamp = pd.to_datetime(row["timestamp"], utc=True).to_pydatetime()
        date_value = timestamp.date()

        pollution = (
            session.query(PollutionMeasurement)
            .filter(PollutionMeasurement.geo_point_id == geo_point.id)
            .one_or_none()
        )
        if not pollution:
            pollution = PollutionMeasurement(geo_point_id=geo_point.id)
        _apply_pollutant_columns(pollution, row.get("pollutant_payload") or [])
        pollution.score = _safe_float(row.get("composite_quality"))
        pollution.date = date_value
        session.add(pollution)

        weather = (
            session.query(WeatherMeasurement)
            .filter(WeatherMeasurement.geo_point_id == geo_point.id)
            .one_or_none()
        )
        if not weather:
            weather = WeatherMeasurement(geo_point_id=geo_point.id)
        weather.temperature_real = _safe_float(row.get("weather_temperature_c"))
        weather.temperature_feels_like = _safe_float(row.get("weather_temperature_c"))
        weather.humidity = _safe_float(row.get("weather_humidity"))
        weather.wind_direction = _safe_float(row.get("weather_wind_direction"))
        weather.wind_speed = _safe_float(row.get("weather_wind_speed_ms"))
        weather.pressure = _safe_float(row.get("weather_pressure_hpa"))
        weather.cloud_direction = _safe_float(row.get("weather_wind_direction"))
        weather.score = _safe_float(row.get("weather_quality"))
        weather.date = date_value
        session.add(weather)

        inserted += 1
    session.commit()
    logger.info("Persisted %s merged measurements", inserted)


def run_pipeline(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    realtime: bool | None = None,
    window_hours: int | None = None,
):
    settings = get_settings()
    realtime_mode = realtime if realtime is not None else False
    if start_date is None and end_date is None and realtime is None:
        realtime_mode = True

    client = DataGouvClient(settings)
    window_hours = window_hours or settings.realtime_window_hours

    if realtime_mode:
        logger.info("Realtime mode enabled (last %s hours)", window_hours)
        window_end = _ensure_utc_timestamp(pd.Timestamp.now(tz="UTC"))
        window_start = window_end - pd.Timedelta(hours=window_hours)
        pollution_raw = client.fetch_latest_pollution_measurements(window_hours=window_hours)
    else:
        history_window = pd.Timedelta(days=settings.max_history_days)
        end_date = end_date or _parse_date(settings.default_end_date)
        earliest_allowed = end_date - history_window
        if start_date is None:
            if settings.default_start_date:
                start_candidate = _parse_date(settings.default_start_date)
            else:
                start_candidate = earliest_allowed
        else:
            start_candidate = start_date
        if start_candidate < earliest_allowed:
            logger.info(
                "Clamping start_date to %s to respect the %s-day retention policy.",
                earliest_allowed,
                settings.max_history_days,
            )
            start_candidate = earliest_allowed
        start_date = start_candidate
        if start_date > end_date:
            raise ValueError("The start date must be before the end date.")
        window_start = _ensure_utc_timestamp(start_date)
        window_end = _ensure_utc_timestamp(end_date)
        pollution_raw = client.fetch_pollution_measurements(start_date, end_date)

    pollution_clean = prepare_pollution_dataframe(pollution_raw)
    pollution_clean = pollution_clean[
        (pollution_clean["timestamp"] >= window_start) & (pollution_clean["timestamp"] <= window_end)
    ]
    metadata_df = client.fetch_station_metadata()
    pollution_with_coords = attach_station_metadata(pollution_clean, metadata_df)
    aggregated_pollution = aggregate_pollution(pollution_with_coords)

    logger.info("Fetching weather SYNOP archive...")
    weather_raw = client.fetch_weather_measurements()
    weather_clean = prepare_weather_dataframe(weather_raw)
    weather_filtered = weather_clean[
        (weather_clean["timestamp"] >= window_start) & (weather_clean["timestamp"] <= window_end)
    ]
    if weather_filtered.empty:
        logger.warning(
            "No weather rows found between %s and %s. "
            "Falling back to sample weather data.",
            window_start,
            window_end,
        )
        sample_weather = pd.read_csv(settings.sample_weather_path, sep=";", dtype=str)
        weather_sample_clean = prepare_weather_dataframe(sample_weather)
        weather_filtered = weather_sample_clean

    logger.info("Building geospatial join...")
    joined = match_and_score(
        aggregated_pollution,
        weather_filtered,
        max_distance_km=settings.max_distance_km,
    )

    if joined.empty:
        logger.warning("No rows matched between pollution and weather datasets.")
        return

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        _persist_measurements(session, joined)


def parse_args():
    parser = argparse.ArgumentParser(description="Pollution + weather impact pipeline")
    parser.add_argument("--start-date", dest="start_date", help="YYYY-MM-DD", default=None)
    parser.add_argument("--end-date", dest="end_date", help="YYYY-MM-DD", default=None)
    parser.add_argument(
        "--realtime",
        action="store_true",
        help="Ignore explicit dates and download the last available data window.",
    )
    parser.add_argument(
        "--window-hours",
        type=int,
        default=None,
        help="Lookback window (in hours) when realtime mode is active.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    start = pd.to_datetime(args.start_date, utc=True) if args.start_date else None
    end = pd.to_datetime(args.end_date, utc=True) if args.end_date else None
    run_pipeline(
        start_date=start,
        end_date=end,
        realtime=args.realtime,
        window_hours=args.window_hours,
    )


if __name__ == "__main__":
    main()
