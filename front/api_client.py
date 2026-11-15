"""Client HTTP centralisé vers l'API VéloVille.

À compléter : lire API_URL et API_TIMEOUT_SECONDES, ajouter l'en-tête
Authorization: Bearer <jeton>, lever ErreurApi (message en français)
sur erreur réseau, délai dépassé ou code HTTP d'erreur.
"""
import requests

API_URL = "http://localhost:8000"

class ErreurApi(Exception):
    """Erreur levée lorsque l'API est injoignable ou répond en erreur."""

def _get(endpoint: str):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=5,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        # raise ErreurApi(str(e))
        raise ErreurApi(
            "Une erreur de communication est survenue."
        )
    except requests.Timeout:
        raise ErreurApi(
            "Le serveur met trop de temps à répondre."
        )

    except requests.ConnectionError:
        raise ErreurApi(
            "Impossible de joindre l'API VéloVille."
        )

    except requests.HTTPError:
        raise ErreurApi(
            f"Erreur de l'API ({response.status_code})."
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