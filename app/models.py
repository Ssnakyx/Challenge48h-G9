"""
SQLAlchemy models backing the Postgres database.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Station(Base):
    __tablename__ = "stations"
    __table_args__ = (UniqueConstraint("code", name="uq_station_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    station_type: Mapped[str] = mapped_column(String(32), default="pollution")
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    region: Mapped[Optional[str]] = mapped_column(String(128))
    extra: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    indices: Mapped[List["ImpactIndex"]] = relationship(
        back_populates="station", cascade="all, delete-orphan"
    )
    forecasts: Mapped[List["ImpactForecast"]] = relationship(
        back_populates="station", cascade="all, delete-orphan"
    )


class ImpactIndex(Base):
    __tablename__ = "impact_indices"
    __table_args__ = (
        UniqueConstraint("station_id", "timestamp", name="uq_station_timestamp"),
        Index("ix_impact_indices_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stations.id", ondelete="CASCADE"), index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    composite_index: Mapped[float] = mapped_column(Float, nullable=False)
    pollution_score: Mapped[float] = mapped_column(Float, nullable=False)
    weather_score: Mapped[float] = mapped_column(Float, nullable=False)
    impact_level: Mapped[str] = mapped_column(String(32), nullable=False)
    dominant_pollutant: Mapped[Optional[str]] = mapped_column(String(32))
    dominant_value: Mapped[Optional[float]] = mapped_column(Float)
    pollutant_unit: Mapped[Optional[str]] = mapped_column(String(32))
    pollutant_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    weather_station_code: Mapped[Optional[str]] = mapped_column(String(32))
    weather_station_name: Mapped[Optional[str]] = mapped_column(String(255))
    weather_latitude: Mapped[Optional[float]] = mapped_column(Float)
    weather_longitude: Mapped[Optional[float]] = mapped_column(Float)
    distance_km: Mapped[Optional[float]] = mapped_column(Float)
    weather_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    station: Mapped[Station] = relationship(back_populates="indices")


class ImpactForecast(Base):
    __tablename__ = "impact_forecasts"
    __table_args__ = (
        UniqueConstraint("station_id", "target_timestamp", name="uq_forecast_target"),
        Index("ix_forecasts_target_timestamp", "target_timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False
    )
    target_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    predicted_index: Mapped[float] = mapped_column(Float, nullable=False)
    horizon_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), default="linreg-1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    station: Mapped[Station] = relationship(back_populates="forecasts")
