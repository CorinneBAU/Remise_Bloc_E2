"""Routeur incidents.

À compléter : GET /incidents (filtre statut, pagination) et
PUT /incidents/{incident_id}/statut (rôle exploitant).
"""
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import IncidentOut, PageIncidentsOut

from api.models import Incident

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)


@router.get(
    "",
    response_model=PageIncidentsOut,
)
def lire_incidents(
    statut: str | None = None,
    page: int = Query(1, ge=1),
    taille_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    requete = db.query(Incident)

    if statut:
        requete = requete.filter(
            Incident.statut == statut
        )

    total = requete.count()

    incidents = (
        requete
        .order_by(
            Incident.date_signalement.desc()
        )
        .offset((page - 1) * taille_page)
        .limit(taille_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "taille_page": taille_page,
        "resultats": incidents,
}