"""
SQLAlchemy models describing the simplified schema requested by the brief.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class GeoPoint(Base):
    """
    Table #3 - geographic point and timestamp that link weather and pollution datasets.
    """

    __tablename__ = "geo_points"
    __table_args__ = (
        UniqueConstraint(
            "station_code",
            "timestamp",
            name="uq_geo_point_station_timestamp",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_code: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    station_name: Mapped[Optional[str]] = mapped_column(String(255))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    weather_measurements: Mapped[List["WeatherMeasurement"]] = relationship(
        back_populates="geo_point", cascade="all, delete-orphan"
    )
    pollution_measurements: Mapped[List["PollutionMeasurement"]] = relationship(
        back_populates="geo_point", cascade="all, delete-orphan"
    )


class WeatherMeasurement(Base):
    """
    Table #1 - weather snapshot aligned to the geo point.
    """

    __tablename__ = "weather_measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geo_point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("geo_points.id", ondelete="CASCADE"), index=True
    )
    temperature_real: Mapped[Optional[float]] = mapped_column(Float)
    temperature_feels_like: Mapped[Optional[float]] = mapped_column(Float)
    humidity: Mapped[Optional[float]] = mapped_column(Float)
    wind_direction: Mapped[Optional[float]] = mapped_column(Float)
    wind_speed: Mapped[Optional[float]] = mapped_column(Float)
    pressure: Mapped[Optional[float]] = mapped_column(Float)
    cloud_direction: Mapped[Optional[float]] = mapped_column(Float)
    score: Mapped[Optional[float]] = mapped_column(Float)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    geo_point: Mapped[GeoPoint] = relationship(back_populates="weather_measurements")


class PollutionMeasurement(Base):
    """
    Table #2 - pollution payload + composite score (0 -> mauvais, 10 -> bon).
    """

    __tablename__ = "pollution_measurements"
    __table_args__ = (
        UniqueConstraint("geo_point_id", name="uq_pollution_geo_point"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geo_point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("geo_points.id", ondelete="CASCADE"), index=True
    )
    pollutant_concentrations: Mapped[Optional[list]] = mapped_column(JSON)
    score: Mapped[Optional[float]] = mapped_column(Float)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    geo_point: Mapped[GeoPoint] = relationship(back_populates="pollution_measurements")
