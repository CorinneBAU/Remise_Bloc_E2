"""Routeur incidents.

À compléter : GET /incidents (filtre statut, pagination) et
PUT /incidents/{incident_id}/statut (rôle exploitant).
"""
from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Incident
from api.schemas import IncidentOut

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)


@router.get(
    "",
    response_model=list[IncidentOut],
)
def lire_incidents(
    db: Session = Depends(get_db),
):
    return db.query(Incident).all()