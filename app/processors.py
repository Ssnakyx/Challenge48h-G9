"""
Pandas-heavy transformations for cleaning, joining and scoring the datasets.
"""

from __future__ import annotations

import logging
import math
import unicodedata
from datetime import datetime
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from .constants import (
    EARTH_RADIUS_KM,
    IMPACT_LEVELS,
    METADATA_LATITUDE_KEYS,
    METADATA_LONGITUDE_KEYS,
    POLLUTANT_THRESHOLDS,
    POLLUTANT_WEIGHTS,
    WEATHER_WEIGHTS,
    POLLUTION_COLUMNS,
)

logger = logging.getLogger(__name__)


def _normalize_column_name(value: str) -> str:
    if not isinstance(value, str):
        return value
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower()
    normalized = normalized.replace("’", "'")
    normalized = "".join(ch if ch.isalnum() else "_" for ch in normalized)
    normalized = "_".join(filter(None, normalized.split("_")))
    return normalized.strip("_")


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={c: _normalize_column_name(c) for c in df.columns})


def prepare_pollution_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw CSV export."""

    df = _rename_columns(df)
    rename_map = {
        col: POLLUTION_COLUMNS[col]
        for col in df.columns
        if col in POLLUTION_COLUMNS
    }
    df = df.rename(columns=rename_map)
    df["timestamp"] = pd.to_datetime(df["period_end"], errors="coerce", utc=True)
    if "period_start" in df.columns:
        df["period_start"] = pd.to_datetime(df["period_start"], errors="coerce", utc=True)
    else:
        df["period_start"] = df["timestamp"] - pd.Timedelta(hours=1)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["raw_value"] = pd.to_numeric(df.get("raw_value"), errors="coerce")
    df["pollutant"] = df["pollutant"].str.upper().str.strip()
    df["station_code"] = df["station_code"].astype(str).str.strip()
    df["station_name"] = df["station_name"].astype(str).str.strip()
    df["unit"] = df.get("unit", pd.Series(["ug/m3"] * len(df))).astype(str).str.strip()
    df = df.dropna(subset=["station_code", "timestamp", "value"])
    return df


def prepare_metadata_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = _rename_columns(df)
    rename_map = {}
    station_code_candidates = (
        "code_site",
        "code_point_prelevement",
        "codesite",
        "code_point_de_prelevement",
        "code_station",
        "natlstationcode",
        "localid",
        "eustationcode",
    )
    for candidate in station_code_candidates:
        if candidate in df.columns:
            rename_map[candidate] = "station_code"
            break
    station_name_candidates = (
        "nom_site",
        "nom_point_prelevement",
        "nom",
        "nom_point_de_prelevement",
        "name",
    )
    for candidate in station_name_candidates:
        if candidate in df.columns:
            rename_map[candidate] = "station_name"
            break
    if "region" in df.columns:
        rename_map["region"] = "region"
    elif "municipality" in df.columns:
        rename_map["municipality"] = "region"
    df = df.rename(columns=rename_map)

    lat_col = next((c for c in df.columns if c in METADATA_LATITUDE_KEYS), None)
    lon_col = next((c for c in df.columns if c in METADATA_LONGITUDE_KEYS), None)
    if not lat_col or not lon_col:
        raise ValueError("Latitude/Longitude columns were not found in metadata file.")

    keep_cols = ["station_code", "station_name", "region", lat_col, lon_col]
    keep_cols = [col for col in keep_cols if col in df.columns]
    if "station_code" not in keep_cols:
        raise ValueError("Station code column could not be identified in metadata.")
    df = df[keep_cols].drop_duplicates(subset=["station_code"])
    df = df.rename(columns={lat_col: "latitude", lon_col: "longitude"})
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    return df


def attach_station_metadata(
    pollution_df: pd.DataFrame, metadata_df: pd.DataFrame
) -> pd.DataFrame:
    metadata_df = prepare_metadata_dataframe(metadata_df)
    metadata_df = metadata_df.rename(
        columns={
            "station_name": "station_name_metadata",
            "region": "region_metadata",
            "latitude": "latitude_metadata",
            "longitude": "longitude_metadata",
        }
    )
    merged = pollution_df.merge(metadata_df, on="station_code", how="left")
    for target, source in [
        ("station_name", "station_name_metadata"),
        ("region", "region_metadata"),
        ("latitude", "latitude_metadata"),
        ("longitude", "longitude_metadata"),
    ]:
        if source in merged.columns:
            base = merged.get(
                target, pd.Series(index=merged.index, dtype=merged[source].dtype)
            )
            merged[target] = base.fillna(merged[source])
            merged = merged.drop(columns=[source])
    missing_coords = merged["latitude"].isna().sum()
    if missing_coords:
        logger.warning("Missing coordinates for %s pollution rows", missing_coords)
    return merged


def _pollutant_payload(group: pd.DataFrame) -> List[dict]:
    payload = []
    for _, row in group.iterrows():
        payload.append(
            {
                "pollutant": row["pollutant"],
                "value": row["value"],
                "unit": row["unit"],
                "weight": row["weight"],
                "threshold": row["threshold"],
                "score": row["score"],
            }
        )
    return payload


def aggregate_pollution(pollution_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate pollutant measurements per station and hour."""

    pollution_df = pollution_df.dropna(subset=["latitude", "longitude"]).copy()
    pollution_df["weight"] = pollution_df["pollutant"].map(POLLUTANT_WEIGHTS).fillna(0.05)
    default_threshold = pollution_df["value"].median() or 1.0
    pollution_df["threshold"] = pollution_df["pollutant"].map(POLLUTANT_THRESHOLDS).fillna(
        default_threshold
    )
    pollution_df["normalized"] = pollution_df["value"] / pollution_df["threshold"]
    pollution_df["score"] = pollution_df["weight"] * pollution_df["normalized"]

    def _aggregate(group: pd.DataFrame) -> pd.Series:
        station_code, timestamp = group.name
        if group["normalized"].notna().any():
            dominant_idx = group["normalized"].idxmax()
        else:
            dominant_idx = group.index[0]
        dominant = group.loc[dominant_idx]
        station_name = (
            group["station_name"].iloc[0]
            if "station_name" in group
            else station_code
        )
        region_value = group["region"].iloc[0] if "region" in group else None
        latitude = group["latitude"].iloc[0] if "latitude" in group else None
        longitude = group["longitude"].iloc[0] if "longitude" in group else None
        return pd.Series(
            {
                "station_code": station_code,
                "station_name": station_name,
                "region": region_value,
                "timestamp": timestamp,
                "latitude": latitude,
                "longitude": longitude,
                "pollution_score": group["score"].sum(),
                "dominant_pollutant": dominant["pollutant"],
                "dominant_value": dominant["value"],
                "pollutant_unit": dominant["unit"],
                "pollutant_payload": _pollutant_payload(group),
            }
        )

    grouped = pollution_df.groupby(["station_code", "timestamp"], group_keys=False)
    try:
        aggregated = grouped.apply(_aggregate, include_groups=False).reset_index(drop=True)
    except TypeError:
        aggregated = grouped.apply(_aggregate).reset_index(drop=True)
    return aggregated


def prepare_weather_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = _rename_columns(df)
    rename_map = {
        "lat": "latitude",
        "lon": "longitude",
        "name": "station_name",
        "geo_id_wmo": "station_code",
        "validity_time": "timestamp",
        "t": "temperature_k",
        "u": "humidity",
        "ff": "wind_speed_ms",
        "dd": "wind_direction",
        "rr1": "precipitation_mm",
        "pmer": "pressure_pa",
    }
    df = df.rename(columns=rename_map)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["temperature_c"] = (
        pd.to_numeric(df.get("temperature_k", pd.Series(dtype=float)), errors="coerce") - 273.15
    )
    df["humidity"] = pd.to_numeric(
        df.get("humidity", pd.Series(dtype=float)), errors="coerce"
    )
    df["wind_speed_ms"] = pd.to_numeric(
        df.get("wind_speed_ms", pd.Series(dtype=float)), errors="coerce"
    )
    df["precipitation_mm"] = pd.to_numeric(
        df.get("precipitation_mm", pd.Series(dtype=float)), errors="coerce"
    )
    df["pressure_hpa"] = (
        pd.to_numeric(df.get("pressure_pa", pd.Series(dtype=float)), errors="coerce") / 100.0
    )
    df = df.dropna(subset=["timestamp", "latitude", "longitude"])
    return df[
        [
            "station_code",
            "station_name",
            "timestamp",
            "latitude",
            "longitude",
            "temperature_c",
            "humidity",
            "wind_speed_ms",
            "wind_direction",
            "precipitation_mm",
            "pressure_hpa",
        ]
    ]


def _compute_weather_score(row: pd.Series) -> float:
    components = []
    temperature = row.get("weather_temperature_c")
    if pd.notna(temperature):
        components.append(
            max(0.0, (temperature - 20.0) / 15.0) * WEATHER_WEIGHTS["temperature"]
        )
    humidity = row.get("weather_humidity")
    if pd.notna(humidity):
        components.append((humidity / 100.0) * WEATHER_WEIGHTS["humidity"])
    wind = row.get("weather_wind_speed_ms")
    if pd.notna(wind):
        components.append((1 - min(wind / 10.0, 1.0)) * WEATHER_WEIGHTS["wind"])
    rain = row.get("weather_precipitation_mm")
    if pd.notna(rain):
        components.append((1 - min(rain / 5.0, 1.0)) * WEATHER_WEIGHTS["precipitation"])
    return float(sum(components))


def _classify_index(value: float) -> str:
    for start, end, label in IMPACT_LEVELS:
        if start <= value < end:
            return label
    return IMPACT_LEVELS[-1][2]


def match_and_score(
    pollution_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    max_distance_km: float = 75.0,
) -> pd.DataFrame:
    """Match aggregated pollution rows with their nearest weather station."""

    if pollution_df.empty or weather_df.empty:
        return pd.DataFrame()

    pollution_df = pollution_df.copy()
    weather_df = weather_df.copy()
    pollution_df["timestamp"] = pd.to_datetime(pollution_df["timestamp"], utc=True)
    weather_df["timestamp"] = pd.to_datetime(weather_df["timestamp"], utc=True)
    pollution_df["timestamp_hour"] = pollution_df["timestamp"].dt.floor("h")
    weather_df["timestamp_hour"] = weather_df["timestamp"].dt.floor("h")

    matches: List[pd.DataFrame] = []

    for timestamp, chunk in pollution_df.groupby("timestamp_hour"):
        weather_chunk = weather_df[weather_df["timestamp_hour"] == timestamp]
        if weather_chunk.empty:
            weather_chunk = weather_df.copy()
            weather_chunk = weather_chunk.assign(
                time_diff=(weather_chunk["timestamp"] - timestamp).abs()
            )
            weather_chunk = (
                weather_chunk.sort_values("time_diff")
                .drop_duplicates(subset=["station_code"])
                .drop(columns=["time_diff"])
                .reset_index(drop=True)
            )
            if weather_chunk.empty:
                continue
        weather_chunk = weather_chunk.reset_index(drop=True)
        chunk = chunk.reset_index(drop=True)
        coords_weather = np.radians(weather_chunk[["latitude", "longitude"]])
        coords_pollution = np.radians(chunk[["latitude", "longitude"]])
        tree = BallTree(coords_weather, metric="haversine")
        distances, indices = tree.query(coords_pollution, k=1)
        distance_km = distances[:, 0] * EARTH_RADIUS_KM
        mask = distance_km <= max_distance_km
        if np.any(mask):
            pollution_match = chunk.loc[mask].copy().reset_index(drop=True)
            weather_match = weather_chunk.iloc[indices[mask, 0]].reset_index(drop=True)
            pollution_match["distance_km"] = distance_km[mask]
        else:
            # fallback: use nearest neighbors ignoring distance threshold
            pollution_match = chunk.copy().reset_index(drop=True)
            weather_match = weather_chunk.iloc[indices[:, 0]].reset_index(drop=True)
            pollution_match["distance_km"] = distance_km

        missing_mask = pollution_match["station_code"].isna()
        if missing_mask.any():
            pollution_match.loc[missing_mask, "station_code"] = pollution_match.loc[
                missing_mask
            ].apply(
                lambda row: f"alias_{round(row['latitude'], 3)}_{round(row['longitude'], 3)}",
                axis=1,
            )

        for column in [
            "station_code",
            "station_name",
            "latitude",
            "longitude",
            "temperature_c",
            "humidity",
            "wind_speed_ms",
            "wind_direction",
            "precipitation_mm",
            "pressure_hpa",
        ]:
            source = weather_match[column].values
            pollution_match[f"weather_{column}"] = source

        matches.append(pollution_match)

    if not matches:
        return pd.DataFrame()

    joined = pd.concat(matches, ignore_index=True)
    joined["weather_score"] = joined.apply(_compute_weather_score, axis=1)
    joined["composite_index"] = (
        (joined["pollution_score"] * 0.65) + (joined["weather_score"] * 0.35)
    ) * 20
    joined["composite_index"] = joined["composite_index"].clip(0, 100)
    joined["impact_level"] = joined["composite_index"].apply(_classify_index)
    return joined.drop(columns=["timestamp_hour"])
