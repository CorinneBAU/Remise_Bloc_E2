"""Routeur stations.

À compléter : GET /stations (filtre commune, pagination) et GET /stations/{station_id}.
"""

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi import Query

from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Station
from api.schemas import PageStationsOut, StationOut
from api.securite import utilisateur_courant

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
    dependencies=[
        Depends(utilisateur_courant)
    ],
)


@router.get(
    "",
    # response_model=list[StationOut],
    response_model=PageStationsOut,
)
def lire_stations(
    commune: str | None = None,
    page: int = Query(1, ge=1),
    taille_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    requete = db.query(Station)
    if commune:
        requete = requete.filter(
            Station.commune == commune
        )

    total = requete.count()

    stations = (
    requete
    .order_by(Station.station_id)
    .offset((page - 1) * taille_page)
    .limit(taille_page)
    .all()
)
    
    return {
    "total": total,
    "page": page,
    "taille_page": taille_page,
    "resultats": stations,
}

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