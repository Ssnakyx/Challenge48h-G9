"""
Pydantic schemas exposed by the FastAPI layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StationOut(BaseModel):
    id: int
    code: str
    name: Optional[str]
    station_type: str = Field(default="pollution")
    latitude: Optional[float]
    longitude: Optional[float]
    region: Optional[str]

    model_config = {"from_attributes": True}


class WeatherSnapshot(BaseModel):
    station_code: Optional[str]
    station_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    distance_km: Optional[float]
    details: Optional[dict]


class PollutantOut(BaseModel):
    pollutant: str
    value: Optional[float]
    unit: Optional[str]
    weight: Optional[float]
    threshold: Optional[float]
    score: Optional[float]


class ImpactIndexOut(BaseModel):
    id: int
    timestamp: datetime
    composite_index: float
    impact_level: str
    pollution_score: float
    weather_score: float
    dominant_pollutant: Optional[str]
    dominant_value: Optional[float]
    pollutant_unit: Optional[str]
    pollutants: List[PollutantOut]
    station: StationOut
    weather: WeatherSnapshot

    model_config = {"from_attributes": True}


class ForecastOut(BaseModel):
    id: int
    station: StationOut
    target_timestamp: datetime
    predicted_index: float
    horizon_hours: int
    model_version: str

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    total_indices: int
    total_forecasts: int
