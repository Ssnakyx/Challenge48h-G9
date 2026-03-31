"""
FastAPI layer exposing the simplified pollution/weather tables.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session, joinedload

from .config import get_settings
from .db import get_session
from .models import GeoPoint, PollutionMeasurement, WeatherMeasurement
from .schemas import HealthResponse, PollutionMeasurementOut, WeatherMeasurementOut

settings = get_settings()
app = FastAPI(
    title="Indice Meteo-Pollution",
    version="2.0.0",
    description="Pipeline météo + pollution (structure simplifiée)",
)


@app.get("/health", response_model=HealthResponse)
def health(session: Session = Depends(get_session)) -> HealthResponse:
    pollution_rows = session.query(PollutionMeasurement).count()
    weather_rows = session.query(WeatherMeasurement).count()
    return HealthResponse(
        status="ok",
        total_pollution_rows=pollution_rows,
        total_weather_rows=weather_rows,
    )


@app.get("/pollution", response_model=List[PollutionMeasurementOut])
def list_pollution_scores(
    limit: int = Query(50, ge=1, le=500),
    station_code: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
) -> List[PollutionMeasurementOut]:
    query = (
        session.query(PollutionMeasurement)
        .options(joinedload(PollutionMeasurement.geo_point))
        .join(PollutionMeasurement.geo_point)
        .order_by(GeoPoint.timestamp.desc())
    )
    if station_code:
        query = query.filter(GeoPoint.station_code == station_code)
    return query.limit(limit).all()


@app.get("/weather", response_model=List[WeatherMeasurementOut])
def list_weather(
    limit: int = Query(50, ge=1, le=500),
    station_code: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
) -> List[WeatherMeasurementOut]:
    query = (
        session.query(WeatherMeasurement)
        .options(joinedload(WeatherMeasurement.geo_point))
        .join(WeatherMeasurement.geo_point)
        .order_by(GeoPoint.timestamp.desc())
    )
    if station_code:
        query = query.filter(GeoPoint.station_code == station_code)
    return query.limit(limit).all()
