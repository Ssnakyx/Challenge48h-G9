"""
Configuration helpers powered by pydantic-settings.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        default="sqlite:///data/air_quality.db",
        alias="DATABASE_URL",
    )
    pollution_bucket: str = Field(
        default="https://object.data.gouv.fr/ineris-prod",
        alias="POLLUTION_BUCKET",
    )
    pollution_prefix: str = Field(
        default="lcsqa/concentrations-de-polluants-atmospheriques-reglementes/temps-reel/",
        alias="POLLUTION_PREFIX",
    )
    pollution_metadata_url: str = Field(
        default="https://static.data.gouv.fr/resources/donnees-temps-reel-de-mesure-des-concentrations-de-polluants-atmospheriques-reglementes-1/20251210-084445/fr-2025-d-lcsqa-ineris-20251209.xls",
        alias="POLLUTION_METADATA_URL",
    )
    weather_resource_url: str = Field(
        default="https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/OBS/SYNOP/synop_2026.csv.gz",
        alias="WEATHER_RESOURCE_URL",
    )
    default_start_date: Optional[str] = Field(
        default=None,
        alias="DEFAULT_START_DATE",
    )
    default_end_date: Optional[str] = Field(
        default=None,
        alias="DEFAULT_END_DATE",
    )
    max_history_days: int = Field(
        default=15,
        alias="MAX_HISTORY_DAYS",
    )
    max_distance_km: float = Field(default=75.0, alias="MAX_DISTANCE_KM")
    forecast_horizon_hours: int = Field(default=6, alias="FORECAST_HORIZON_HOURS")
    realtime_window_hours: int = Field(default=24, alias="REALTIME_WINDOW_HOURS")
    sample_pollution_path: Path = Field(
        default=Path("data") / "sample_pollution.csv",
        alias="SAMPLE_POLLUTION_PATH",
    )
    sample_metadata_path: Path = Field(
        default=Path("data") / "sample_metadata.csv",
        alias="SAMPLE_METADATA_PATH",
    )
    sample_weather_path: Path = Field(
        default=Path("data") / "sample_weather.csv",
        alias="SAMPLE_WEATHER_PATH",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached configuration so we do not re-parse the environment."""

    return Settings()
