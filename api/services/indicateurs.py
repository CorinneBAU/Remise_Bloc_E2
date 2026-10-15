"""Calcul des trois indicateurs (module métier testé).

À compléter : activite_par_jour(session, date_debut, date_fin),
stations_actives(session, limite) et incidents_par_statut(session).
Les routeurs ne font qu'appeler ces fonctions.
"""

from sqlalchemy import func

from api.models import Trajet
from api.models import Incident


def activite_par_jour(session):

    lignes = (
        session.query(
            func.date(Trajet.depart_horodatage),
            func.count(Trajet.trajet_id),
        )
        .group_by(
            func.date(
                Trajet.depart_horodatage
            )
        )
        .all()
    )

    return [
        {
            "jour": str(ligne[0]),
            "nb_trajets": ligne[1],
        }
        for ligne in lignes
    ]


def stations_actives(
    session,
    limite: int = 10,
):

    lignes = (
        session.query(
            Trajet.station_depart,
            func.count(
                Trajet.trajet_id
            ).label("nb_trajets"),
        )
        .group_by(
            Trajet.station_depart
        )
        .order_by(
            func.count(
                Trajet.trajet_id
            ).desc()
        )
        .limit(limite)
        .all()
    )

    return [
        {
            "station": ligne[0],
            "nb_trajets": ligne[1],
        }
        for ligne in lignes
    ]


def incidents_par_statut(session):

    lignes = (
        session.query(
            Incident.statut,
            func.count(
                Incident.incident_id
            ).label("nb_incidents"),
        )
        .group_by(
            Incident.statut
        )
        .all()
    )

    return [
        {
            "statut": ligne[0],
            "nb_incidents": ligne[1],
        }
        for ligne in lignes
    ]