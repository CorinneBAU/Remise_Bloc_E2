"""Client HTTP centralisé vers l'API VéloVille.

À compléter : lire API_URL et API_TIMEOUT_SECONDES, ajouter l'en-tête
Authorization: Bearer <jeton>, lever ErreurApi (message en français)
sur erreur réseau, délai dépassé ou code HTTP d'erreur.
"""
import requests
import os
import streamlit as st

from dotenv import load_dotenv

load_dotenv()

# API_URL = "http://localhost:8000"
API_URL = os.getenv("API_URL")
API_TIMEOUT_SECONDES = int(
    os.getenv("API_TIMEOUT_SECONDES", "5")
)

def _headers() -> dict:

    token = st.session_state.get("token")

    if token:
        return {
            "Authorization": f"Bearer {token}"
        }

    return {}

class ErreurApi(Exception):
    """Erreur levée lorsque l'API est injoignable ou répond en erreur."""

def _get(endpoint: str):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            # timeout=5,
            headers=_headers(),
            timeout=API_TIMEOUT_SECONDES,
        )

        response.raise_for_status()

        return response.json()

    except requests.Timeout:    
        raise ErreurApi(
            "Le serveur met trop de temps à répondre."
        )

    except requests.ConnectionError:
        raise ErreurApi(
            "Impossible de joindre l'API VéloVille."
        )
   
    
    except requests.HTTPError:

            # except requests.RequestException as e:
            #     # raise ErreurApi(str(e))
            if response.status_code == 401:
                raise ErreurApi(
                    "Authentification requise. Veuillez vous reconnecter."
                )

            if response.status_code == 403:
                raise ErreurApi(
                    "Vous n'êtes pas autorisé à effectuer cette action."
                )
                
            raise ErreurApi(
                f"Erreur de l'API ({response.status_code})."
                )

    except requests.RequestException:
        raise ErreurApi(
            "Une erreur de communication est survenue."
        )    
           
    
    
def lister_stations(
    commune=None,
    page=1,
    taille_page=20,
):
    params = []

    if commune:
        params.append(f"commune={commune}")

    params.append(f"page={page}")
    params.append(f"taille_page={taille_page}")

    query = "&".join(params)

    return _get(f"/stations?{query}")

def lister_trajets():
    return _get("/trajets")

def lister_incidents():
    return _get("/incidents")

def activite_par_jour():
    return _get("/indicateurs/activite-par-jour")

def stations_actives():
    return _get("/indicateurs/stations-actives")

def incidents_par_statut():
    return _get("/indicateurs/incidents-par-statut")