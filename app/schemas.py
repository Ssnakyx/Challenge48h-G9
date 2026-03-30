"""
Pydantic schemas (FastAPI responses) reflecting the simplified data model.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class GeoPointOut(BaseModel):
    id: int
    station_code: Optional[str]
    station_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    timestamp: datetime
    date: date

    model_config = {"from_attributes": True}


class WeatherMeasurementOut(BaseModel):
    id: int
    temperature_real: Optional[float]
    temperature_feels_like: Optional[float]
    humidity: Optional[float]
    wind_direction: Optional[float]
    wind_speed: Optional[float]
    pressure: Optional[float]
    cloud_direction: Optional[float]
    score: Optional[float]
    date: date
    geo_point: GeoPointOut

    model_config = {"from_attributes": True}


class PollutionMeasurementOut(BaseModel):
    id: int
    pollutant_concentrations: Optional[list]
    score: Optional[float]
    date: date
    geo_point: GeoPointOut

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    total_pollution_rows: int
    total_weather_rows: int
