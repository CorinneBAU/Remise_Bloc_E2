"""Routeur trajets.

À compléter : GET /trajets (filtres date_debut, date_fin, station ; pagination).
"""
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from sqlalchemy.orm import Session
from sqlalchemy import func

from datetime import date

from api.database import get_db
from api.schemas import TrajetOut, PageTrajetsOut
from api.models import Trajet
from api.securite import utilisateur_courant


router = APIRouter(
    prefix="/trajets",
    tags=["trajets"],
    dependencies=[
        Depends(utilisateur_courant)
    ],
)


@router.get(
    "",
    response_model=PageTrajetsOut,
)
def lire_trajets(
    date_debut: date | None = None,
    date_fin: date | None = None,
    station: str | None = None,
    page: int = Query(1, ge=1),
    taille_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    
    requete = db.query(Trajet)

    if date_debut:
        requete = requete.filter(
            func.date(
                Trajet.depart_horodatage
            ) >= date_debut
        )

    if date_fin:
        requete = requete.filter(
            func.date(
                Trajet.depart_horodatage
            ) <= date_fin
        )

    if station:
        requete = requete.filter(
            (Trajet.station_depart == station)
            | (Trajet.station_arrivee == station)
        )

    total = requete.count()

    trajets = (
    requete
    .order_by(
        Trajet.depart_horodatage
    )
    .offset((page - 1) * taille_page)
    .limit(taille_page)
    .all()
)

    return {
    "total": total,
    "page": page,
    "taille_page": taille_page,
    "resultats": trajets,
}