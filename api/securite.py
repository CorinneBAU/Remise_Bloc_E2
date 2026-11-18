"""Authentification et autorisation.

À compléter : vérification d'un mot de passe contre son hachage bcrypt, création et
décodage du JWT (secret et algorithme lus dans l'environnement),
dépendances utilisateur_courant() et exiger_role("exploitant").
"""
import os

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from dotenv import load_dotenv



load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(
    os.getenv("JWT_EXPIRATION_MINUTES", "60")
)
print("JWT_SECRET =", repr(JWT_SECRET))

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