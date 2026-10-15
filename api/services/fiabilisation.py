"""Règles de fiabilisation des données (module métier testé).

À compléter : fonctions pures, sans accès à la base, qui normalisent ou rejettent
une valeur ou une ligne : horodatages, identifiants de vélo, statuts
d'incident, durées, références de station, cohérence des dates,
doublons. Chaque fonction retourne la valeur normalisée ou signale le
motif de rejet. Ces fonctions sont appelées par scripts/importer.py et
couvertes par tests/unit/.
"""
import pandas as pd
from datetime import datetime

# Fonction de normalisation

def normaliser_statut(statut: str) -> str:
    """ Normalise le statut d'un incident
    Exemples :
    - "Ouvert" -> "ouvert"
    - "RESOLU" -> "resolu"
    - "En cours" -> "en_cours"
    """
    if pd.isna(statut):
        return statut
    return statut.lower().replace(" ", "_")

def normaliser_horodatage(horodatage: str) -> datetime | None:
    """ Convertit un horodatage dans un format date
    Retourne None si la valeur n'est pas convertible
    """
    return pd.to_datetime(horodatage, errors="coerce")

def normaliser_velo_id(velo_id: str) -> str:
    """ Normalise un identifiant vélo sous le format "V" suivi de 4 chiffres
    Exemple : 
    - "v1458" -> "V1458"
    """
    return velo_id.upper()


# Fonction de validation

def duree_valide(duree: int) ->  tuple[bool, str | None]:
    """ Vérifie que la durée d'un trajet est strictement positive.
    Précise le motif de rejet "duree_secondes <= 0" en cas d'invalidité
    """
    if duree > 0:
        return True, None

    return False, "duree_secondes <= 0"

def statut_valide(statut: str) -> tuple[bool, str | None]:
    """Vérifie que le statut correspond à l'un des états de traitement autorisés :
    - ouvert
    - en_cours
    - resolu
    Précise le motif de rejet "statut invalide" en cas d'invalidité
    """
    if statut in {
        "ouvert",
        "en_cours",
        "resolu"
    }:
        return True, None

    return False, "statut invalide"

def capacite_valide(capacite: int) -> tuple[bool, str | None]:
    """ Vérifie si la capacité d'une station est > 0
    Précise le motif de rejet "capacite station <= 0" en cas d'invalidité
    """
    if capacite > 0:
        return True, None

    return False, "capacite station <= 0"

def date_coherente(date_signalement: datetime, date_resolution: datetime | None) -> tuple[bool, str | None]:
    """Vérifie la cohérence des dates d'incident.
    La date de résolution doit être postérieure ou égale à la date de signalement.
    Une date de résolution vide est acceptée.
    Précise le motif de rejet "date_resolution < date_signalement" en cas d'invalidité
    """
    if pd.isna(date_resolution):
        return True, None
    
    if date_resolution >= date_signalement:
        return True, None

    return False, "date_resolution < date_signalement"

def station_referencee(station_id: str, stations_liste: set[str])-> tuple[bool, str | None]:
    """Vérifie que la station existe bien dans le fichier stations.csv
     Précise le motif de rejet "station inexistante dans stations.csv" en cas d'invalidité
    """
    if station_id in stations_liste:
        return True, None

    return False, "station inexistante dans stations.csv"
    

