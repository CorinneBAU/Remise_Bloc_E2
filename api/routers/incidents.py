"""Routeur incidents.

À compléter : GET /incidents (filtre statut, pagination) et
PUT /incidents/{incident_id}/statut (rôle exploitant).
"""
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import HTTPException

from datetime import datetime

from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import IncidentOut, PageIncidentsOut, ChangementStatutIn

from api.models import Incident
from api.securite import exiger_role
from api.securite import utilisateur_courant



router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
    dependencies=[
            Depends(utilisateur_courant)
        ],
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

@router.put(
    "/{incident_id}/statut",
    response_model=IncidentOut,
    dependencies=[
        Depends(exiger_role("exploitant"))
    ],
)
def modifier_statut_incident(
    incident_id: str,
    changement: ChangementStatutIn,
    db: Session = Depends(get_db),
):
    incident = (
        db.query(Incident)
        .filter(
            Incident.incident_id == incident_id
        )
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident introuvable",
        )

    transitions_autorisees = {
        "ouvert": ["en_cours", "resolu"],
        "en_cours": ["resolu"],
        "resolu": [],
    }

    if changement.statut not in transitions_autorisees[
        incident.statut
    ]:
        raise HTTPException(
            status_code=422,
            detail="Transition de statut non autorisee",
        )

    incident.statut = changement.statut

    if (
        changement.statut == "resolu"
        and incident.date_resolution is None
    ):
        incident.date_resolution = datetime.now()

    db.commit()
    db.refresh(incident)

    return incident