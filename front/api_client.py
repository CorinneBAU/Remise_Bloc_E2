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
        raise ErreurApi(str(e))
    
def lister_stations():
    return _get("/stations")

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