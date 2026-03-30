"""
FastAPI application exposing the computed indices and forecasts.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_session
from .models import ImpactForecast, ImpactIndex, Station
from .schemas import ForecastOut, HealthResponse, ImpactIndexOut, WeatherSnapshot

settings = get_settings()
app = FastAPI(
    title="Indice Meteo-Pollution",
    version="1.0.0",
    description="Fusion pollution + meteo (Challenge 48h)",
)


def _to_weather_snapshot(row: ImpactIndex) -> WeatherSnapshot:
    return WeatherSnapshot(
        station_code=row.weather_station_code,
        station_name=row.weather_station_name,
        latitude=row.weather_latitude,
        longitude=row.weather_longitude,
        distance_km=row.distance_km,
        details=row.weather_payload,
    )


def _to_index_schema(row: ImpactIndex) -> ImpactIndexOut:
    return ImpactIndexOut(
        id=row.id,
        timestamp=row.timestamp,
        composite_index=row.composite_index,
        impact_level=row.impact_level,
        pollution_score=row.pollution_score,
        weather_score=row.weather_score,
        dominant_pollutant=row.dominant_pollutant,
        dominant_value=row.dominant_value,
        pollutant_unit=row.pollutant_unit,
        pollutant_payload=row.pollutant_payload,
        station=row.station,
        weather=_to_weather_snapshot(row),
    )


@app.get("/health", response_model=HealthResponse)
def health(session: Session = Depends(get_session)) -> HealthResponse:
    total_indices = session.query(ImpactIndex).count()
    total_forecasts = session.query(ImpactForecast).count()
    return HealthResponse(status="ok", total_indices=total_indices, total_forecasts=total_forecasts)


@app.get("/indices", response_model=List[ImpactIndexOut])
def list_indices(
    limit: int = Query(50, ge=1, le=500),
    station_code: Optional[str] = Query(None),
    impact_level: Optional[str] = Query(None),
    session: Session = Depends(get_session),
) -> List[ImpactIndexOut]:
    query = (
        session.query(ImpactIndex)
        .join(ImpactIndex.station)
        .order_by(ImpactIndex.timestamp.desc())
    )
    if station_code:
        query = query.filter(Station.code == station_code)
    if impact_level:
        query = query.filter(ImpactIndex.impact_level == impact_level.lower())
    rows = query.limit(limit).all()
    return [_to_index_schema(row) for row in rows]


@app.get("/stations/{station_code}/indices", response_model=List[ImpactIndexOut])
def station_history(
    station_code: str,
    limit: int = Query(24, ge=1, le=200),
    session: Session = Depends(get_session),
) -> List[ImpactIndexOut]:
    station = session.query(Station).filter(Station.code == station_code).one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Station inconnue")
    rows = (
        session.query(ImpactIndex)
        .filter(ImpactIndex.station_id == station.id)
        .order_by(ImpactIndex.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [_to_index_schema(row) for row in rows]


@app.get("/forecasts", response_model=List[ForecastOut])
def list_forecasts(
    station_code: Optional[str] = Query(None),
    session: Session = Depends(get_session),
) -> List[ForecastOut]:
    query = session.query(ImpactForecast).join(ImpactForecast.station).order_by(
        ImpactForecast.target_timestamp.asc()
    )
    if station_code:
        query = query.filter(Station.code == station_code)
    return query.all()
