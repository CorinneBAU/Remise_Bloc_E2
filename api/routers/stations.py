"""Routeur stations.

À compléter : GET /stations (filtre commune, pagination) et GET /stations/{station_id}.
"""

from fastapi import APIRouter
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