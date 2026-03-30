"""
Command line entry point that drives the ingestion, processing and persistence.
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone
from typing import Dict, Iterable

import pandas as pd

from .config import get_settings
from .data_clients import DataGouvClient
from .db import SessionLocal, engine
from .forecasting import build_forecasts
from .models import Base, ImpactForecast, ImpactIndex, Station
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


def _load_station_cache(session, codes: Iterable[str]) -> Dict[str, Station]:
    codes = {code for code in codes if code}
    if not codes:
        return {}
    existing = (
        session.query(Station)
        .filter(Station.code.in_(list(codes)))
        .all()
    )
    return {station.code: station for station in existing}


def _ensure_station(session, cache: dict, row: pd.Series) -> Station:
    code = row["station_code"]
    station = cache.get(code)
    if station:
        updated = False
        if row.get("station_name") and station.name != row["station_name"]:
            station.name = row["station_name"]
            updated = True
        if row.get("region") and station.region != row["region"]:
            station.region = row["region"]
            updated = True
        lat = _safe_float(row.get("latitude"))
        lon = _safe_float(row.get("longitude"))
        if lat is not None and station.latitude != lat:
            station.latitude = lat
            updated = True
        if lon is not None and station.longitude != lon:
            station.longitude = lon
            updated = True
        if updated:
            session.add(station)
        return station
    station = Station(
        code=code,
        name=row.get("station_name"),
        station_type="pollution",
        latitude=_safe_float(row.get("latitude")),
        longitude=_safe_float(row.get("longitude")),
        region=row.get("region"),
    )
    session.add(station)
    session.flush()
    cache[code] = station
    return station


def _persist_indices(session, df: pd.DataFrame) -> Dict[str, Station]:
    cache = _load_station_cache(session, df["station_code"].unique())
    inserted = 0
    for _, row in df.iterrows():
        station = _ensure_station(session, cache, row)
        timestamp = pd.to_datetime(row["timestamp"], utc=True).to_pydatetime()
        existing = (
            session.query(ImpactIndex)
            .filter(
                ImpactIndex.station_id == station.id,
                ImpactIndex.timestamp == timestamp,
            )
            .one_or_none()
        )
        payload = ImpactIndex(
            station_id=station.id,
            timestamp=timestamp,
            composite_index=_safe_float(row["composite_index"]) or 0.0,
            pollution_score=_safe_float(row["pollution_score"]) or 0.0,
            weather_score=_safe_float(row["weather_score"]) or 0.0,
            impact_level=row.get("impact_level") or "unknown",
            dominant_pollutant=row.get("dominant_pollutant"),
            dominant_value=_safe_float(row.get("dominant_value")),
            pollutant_unit=row.get("pollutant_unit"),
            pollutant_payload=row.get("pollutant_payload"),
            weather_station_code=row.get("weather_station_code"),
            weather_station_name=row.get("weather_station_name"),
            weather_latitude=_safe_float(row.get("weather_latitude")),
            weather_longitude=_safe_float(row.get("weather_longitude")),
            distance_km=_safe_float(row.get("distance_km")),
            weather_payload={
                "temperature_c": _safe_float(row.get("weather_temperature_c")),
                "humidity": _safe_float(row.get("weather_humidity")),
                "wind_speed_ms": _safe_float(row.get("weather_wind_speed_ms")),
                "wind_direction": _safe_float(row.get("weather_wind_direction")),
                "precipitation_mm": _safe_float(row.get("weather_precipitation_mm")),
                "pressure_hpa": _safe_float(row.get("weather_pressure_hpa")),
            },
        )
        if existing:
            for field in [
                "composite_index",
                "pollution_score",
                "weather_score",
                "impact_level",
                "dominant_pollutant",
                "dominant_value",
                "pollutant_unit",
                "pollutant_payload",
                "weather_station_code",
                "weather_station_name",
                "weather_latitude",
                "weather_longitude",
                "distance_km",
                "weather_payload",
            ]:
                setattr(existing, field, getattr(payload, field))
        else:
            session.add(payload)
            inserted += 1
    session.commit()
    logger.info("Persisted %s new impact indices", inserted)
    return cache


def _persist_forecasts(session, df: pd.DataFrame, cache: Dict[str, Station]) -> None:
    if df.empty:
        return
    inserted = 0
    for _, row in df.iterrows():
        station = cache.get(row["station_code"])
        if not station:
            continue
        target_timestamp = pd.to_datetime(row["target_timestamp"], utc=True).to_pydatetime()
        existing = (
            session.query(ImpactForecast)
            .filter(
                ImpactForecast.station_id == station.id,
                ImpactForecast.target_timestamp == target_timestamp,
            )
            .one_or_none()
        )
        payload = ImpactForecast(
            station_id=station.id,
            target_timestamp=target_timestamp,
            predicted_index=_safe_float(row["predicted_index"]) or 0.0,
            horizon_hours=int(row["horizon_hours"]),
            model_version=row.get("model_version") or "linreg-1",
        )
        if existing:
            existing.predicted_index = payload.predicted_index
            existing.horizon_hours = payload.horizon_hours
            existing.model_version = payload.model_version
        else:
            session.add(payload)
            inserted += 1
    session.commit()
    logger.info("Persisted %s forecasts", inserted)


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
        start_date = start_date or _parse_date(settings.default_start_date)
        end_date = end_date or _parse_date(settings.default_end_date)
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
        logger.error(
            "No weather rows found between %s and %s. "
            "Check WEATHER_RESOURCE_URL or adjust your window.",
            window_start,
            window_end,
        )
        raise ValueError(
            "Weather dataset does not contain observations for the requested window."
        )

    logger.info("Building geospatial join...")
    joined = match_and_score(
        aggregated_pollution,
        weather_filtered,
        max_distance_km=settings.max_distance_km,
    )

    if joined.empty:
        logger.warning("No rows matched between pollution and weather datasets.")
        return

    logger.info("Generating forecasts...")
    forecasts = build_forecasts(joined, settings.forecast_horizon_hours)

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        cache = _persist_indices(session, joined)
        _persist_forecasts(session, forecasts, cache)


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
