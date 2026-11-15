"""Calcul des trois indicateurs (module métier testé).

À compléter : activite_par_jour(session, date_debut, date_fin),
stations_actives(session, limite) et incidents_par_statut(session).
Les routeurs ne font qu'appeler ces fonctions.
"""

from sqlalchemy import func

from datetime import date

from api.models import Trajet,Incident,Station


def activite_par_jour(
        session,
        date_debut: date | None = None,
        date_fin: date | None = None,
):

        requete = (
        session.query(
            func.date(
                Trajet.depart_horodatage
            ).label("jour"),

            func.count(
                Trajet.trajet_id
            ).label("nb_trajets"),
        )
    )

        if date_debut:
            requete = requete.filter(
                func.date(
                    Trajet.depart_horodatage
                ) >= date_debut
            )

        if date_fin:
            requete = requete.filter(
                func.date(
                    Trajet.depart_horodatage
                ) <= date_fin
            )

        lignes = (
            requete
            .group_by(
                func.date(
                    Trajet.depart_horodatage
                )
            )
            .order_by(
                func.date(
                    Trajet.depart_horodatage
                )
            )
            .all()
        )

        return {
            "donnees": [
                {
                    "jour": str(ligne[0]),
                    "nb_trajets": ligne[1],
                }
                for ligne in lignes
            ]
}


def stations_actives(
    session,
    limite: int = 10,
):

    mouvements = {}

    # Comptage des départs
    departs = (
        session.query(
            Trajet.station_depart,
            func.count(
                Trajet.trajet_id
            ).label("nb_departs"),
        )
        .group_by(
            Trajet.station_depart
        )
        .all()
    )

    for station_id, nb_departs in departs:
        mouvements[station_id] = {
            "nb_departs": nb_departs,
            "nb_arrivees": 0,
        }

    # Comptage des arrivées
    arrivees = (
        session.query(
            Trajet.station_arrivee,
            func.count(
                Trajet.trajet_id
            ).label("nb_arrivees"),
        )
        .filter(
            Trajet.station_arrivee.isnot(None)
        )
        .group_by(
            Trajet.station_arrivee
        )
        .all()
    )

    for station_id, nb_arrivees in arrivees:
        if station_id not in mouvements:
            mouvements[station_id] = {
                "nb_departs": 0,
                "nb_arrivees": nb_arrivees,
            }
        else:
            mouvements[station_id]["nb_arrivees"] = nb_arrivees

    resultat = []

    for station_id, valeurs in mouvements.items():
        station = (
            session.query(Station)
            .filter(
                Station.station_id == station_id
            )
            .first()
        )

        resultat.append(
            {
                "station_id": station.station_id,
                "nom": station.nom,
                "nb_departs": valeurs["nb_departs"],
                "nb_arrivees": valeurs["nb_arrivees"],
                "total_mouvements": (
                    valeurs["nb_departs"]
                    + valeurs["nb_arrivees"]
                ),
            }
        )

    resultat.sort(
        key=lambda ligne: (
            -ligne["total_mouvements"],
            ligne["station_id"],
        )
    )

    return {
        "donnees": [
            {
                "station_id": ligne["station_id"],
                "nom": ligne["nom"],
                "nb_departs": ligne["nb_departs"],
                "nb_arrivees": ligne["nb_arrivees"],
            }
            for ligne in resultat[:limite]
        ]
}

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

    donnees = [
        {
            "statut": ligne[0],
            "nb_incidents": ligne[1],
        }
        for ligne in lignes
    ]

    incidents_resolus = (
        session.query(Incident)
        .filter(
            Incident.statut == "resolu",
            Incident.date_resolution.isnot(None),
        )
        .all()
    )

    durees = []

    for incident in incidents_resolus:

        duree = (
            incident.date_resolution
            - incident.date_signalement
        )

        durees.append(
            duree.total_seconds() / 3600
        )

    if durees:
        delai_moyen = round(
            sum(durees) / len(durees),
            1
        )
    else:
        delai_moyen = None

    return {
        "donnees": donnees,
        "delai_moyen_resolution_heures": delai_moyen,
    }