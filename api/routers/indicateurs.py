"""Routeur indicateurs.

À compléter : GET /indicateurs/activite-par-jour,
GET /indicateurs/stations-actives et
GET /indicateurs/incidents-par-statut.
"""
from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from api.database import get_db
from api.services.indicateurs import (
    activite_par_jour,
    stations_actives,
    incidents_par_statut,
)

router = APIRouter(
    prefix="/indicateurs",
    tags=["indicateurs"],
)


@router.get(
    "/activite-par-jour"
)
def lire_activite_par_jour(
    db: Session = Depends(get_db),
):
    return activite_par_jour(db)

# @router.get(
#     "/activite-par-jour"
# )
# def lire_activite_par_jour(
#     db: Session = Depends(get_db),
# ):
#     return [
#         {
#             "jour": "2026-08-24",
#             "nb_trajets": 123
#         }
#     ]

@router.get(
    "/stations-actives"
)
def lire_stations_actives(
    db: Session = Depends(get_db),
):
    return stations_actives(db)


@router.get(
    "/incidents-par-statut"
)
def lire_incidents_par_statut(
    db: Session = Depends(get_db),
):
    return incidents_par_statut(db)