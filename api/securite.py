"""Authentification et autorisation.

À compléter : vérification d'un mot de passe contre son hachage bcrypt, création et
décodage du JWT (secret et algorithme lus dans l'environnement),
dépendances utilisateur_courant() et exiger_role("exploitant").
"""
import os

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
)
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import Utilisateur
from dotenv import load_dotenv



load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(
    os.getenv("JWT_EXPIRATION_MINUTES", "60")
)

bearer_scheme = HTTPBearer(
    auto_error=False,
)


def verifier_mot_de_passe(
    mot_de_passe_clair: str,
    mot_de_passe_hash: str,
) -> bool:
    return bcrypt.checkpw(
        mot_de_passe_clair.encode(),
        mot_de_passe_hash.encode(),
    )



def creer_access_token(
    username: str,
    role: str,
) -> str:

    expiration = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=JWT_EXPIRATION_MINUTES
        )
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

def decoder_access_token(
    token: str,
) -> dict:

    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
    )

def utilisateur_courant(
    creds: HTTPAuthorizationCredentials | None =
    Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Utilisateur:

    if creds is None:
        raise HTTPException(
            status_code=401,
            detail="Authentification requise",
        )

    try:
        payload = decoder_access_token(
            creds.credentials
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expiré",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token invalide",
        )

    utilisateur = (
        db.query(Utilisateur)
        .filter(
            Utilisateur.username
            == payload["sub"]
        )
        .first()
    )

    if utilisateur is None:
        raise HTTPException(
            status_code=401,
            detail="Utilisateur inconnu",
        )

    return utilisateur


def exiger_role(role_attendu: str):

    def verifier(
        utilisateur: Utilisateur = Depends(
            utilisateur_courant
        ),
    ) -> Utilisateur:

        if utilisateur.role != role_attendu:
            raise HTTPException(
                status_code=403,
                detail="Role non autorise",
            )

        return utilisateur

    return verifier