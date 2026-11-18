"""Routeur auth.

À compléter : POST /auth/login.
"""


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Utilisateur
from api.schemas import LoginIn
from api.schemas import LoginOut

from api.securite import (
    verifier_mot_de_passe,
    creer_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post(
    "/login",
    response_model=LoginOut,
)
def login(
    donnees: LoginIn,
    db: Session = Depends(get_db),
):

    utilisateur = (
        db.query(Utilisateur)
        .filter(
            Utilisateur.username == donnees.username
        )
        .first()
    )

    if utilisateur is None:
        raise HTTPException(
            status_code=401,
            detail="Identifiants invalides",
        )

    if not verifier_mot_de_passe(
        donnees.password,
        utilisateur.mot_de_passe_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Identifiants invalides",
        )

    token = creer_access_token(
        utilisateur.username,
        utilisateur.role,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": utilisateur.role,
    }