"""Routeur trajets.

À compléter : GET /trajets (filtres date_debut, date_fin, station ; pagination).
"""
from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Trajet
from api.schemas import TrajetOut

router = APIRouter(
    prefix="/trajets",
    tags=["trajets"],
)


@router.get(
    "",
    response_model=list[TrajetOut],
)
def lire_trajets(
    db: Session = Depends(get_db),
):
    return db.query(Trajet).all()