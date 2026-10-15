"""Schémas Pydantic (entrées et sorties de l'API).

À compléter : schémas de lecture des trois ressources, enveloppe paginée, corps de
connexion, réponse de connexion, corps de changement de statut, réponses
des trois indicateurs.
"""
from datetime import date
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# Stations
# ============================================================

class StationOut(BaseModel):
    station_id: str
    nom: str
    commune: str
    capacite: int
    latitude: float
    longitude: float
    date_mise_en_service: date

    model_config = ConfigDict(
        from_attributes=True,
    )


# ============================================================
# Trajets
# ============================================================

class TrajetOut(BaseModel):
    trajet_id: str
    velo_id: str
    depart_horodatage: datetime
    station_depart: str
    station_arrivee: str | None
    duree_secondes: int
    type_usager: str
    usager_ref: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )


# ============================================================
# Incidents
# ============================================================

class IncidentOut(BaseModel):
    incident_id: str
    date_signalement: datetime
    cible: str
    velo_id: str | None
    station_id: str | None
    type_incident: str
    statut: str
    date_resolution: datetime | None
    technicien: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )