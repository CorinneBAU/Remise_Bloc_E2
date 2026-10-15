"""Routeur stations.

À compléter : GET /stations (filtre commune, pagination) et GET /stations/{station_id}.
"""

from fastapi import APIRouter, HTTPException
from fastapi import Depends

from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Station
from api.schemas import StationOut

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
)


@router.get(
    "",
    response_model=list[StationOut],
)
def lire_stations(
    db: Session = Depends(get_db),
):
    return db.query(Station).all()

@router.get(
    "/{station_id}",
    response_model=StationOut,
)
def lire_station(
    station_id: str,
    db: Session = Depends(get_db),
):
    station = (
        db.query(Station)
        .filter(
            Station.station_id == station_id
        )
        .first()
    )

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station introuvable",
        )

    return station