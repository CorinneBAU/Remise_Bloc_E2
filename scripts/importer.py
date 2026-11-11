"""Import et fiabilisation des trois exports CSV dans PostgreSQL.

À compléter : lire data/stations.csv, data/trajets.csv et data/incidents.csv,
appliquer les règles de fiabilisation (api/services/fiabilisation.py),
charger les lignes valides, journaliser les rejets et les avertissements.
Le script doit être idempotent : deux exécutions successives laissent la
base dans le même état.

Usage prévu : python scripts/importer.py [--dossier data]
"""
import pandas as pd
import csv
import logging
import time
from pathlib import Path
from typing import Any
from api.database import SessionLocal
from api.models import Station, Trajet, Incident
from api.services.fiabilisation import station_referencee, duree_valide, normaliser_statut
from sqlalchemy import text


FICHIER_INCIDENTS = "./data/incidents.csv"
FICHIER_STATIONS = "./data/stations.csv"
FICHIER_TRAJETS = "./data/trajets.csv"

FICHIER_REJETS = "sorties/rejets_chargement.csv"

# TAILLE_LOT = 500


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def ecrire_rejets(rejets: list[dict[str, Any]]) -> None:
    """Écrit les lignes rejetées dans un fichier CSV."""

    chemin = Path(FICHIER_REJETS)

    chemin.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    if not rejets:
        if chemin.exists():
            chemin.unlink()
        return

    toutes_cles: list[str] = []

    for rejet in rejets:
        for cle in rejet:
            if cle not in toutes_cles:
                toutes_cles.append(cle)

    with chemin.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as fichier:
        writer = csv.DictWriter(
            fichier,
            fieldnames=toutes_cles,
        )

        writer.writeheader()
        writer.writerows(rejets)


def ajouter_anomalie(
    journal,
    fichier,
    ligne,
    identifiant,
    colonne,
    valeur,
    motif,
    decision,
    categorie=""
):
    journal.append({
        "fichier": fichier,
        "ligne": ligne,
        "identifiant": identifiant,
        "colonne": colonne,
        "valeur": valeur,
        "motif": motif,
        "decision": decision,
        "categorie": categorie
    })

def main() -> None:

    debut_global = time.perf_counter()

    rejets: list[dict[str, Any]] = []
    statistiques: list[dict[str, Any]] = []

    logger.info("Début du chargement veloville.")

    

    stations = pd.read_csv(FICHIER_STATIONS)
    trajets = pd.read_csv(FICHIER_TRAJETS)
    incidents = pd.read_csv(FICHIER_INCIDENTS)

    db = SessionLocal()

    try:

        db.execute(text("DELETE FROM trajet"))
        db.execute(text("DELETE FROM incident"))
        db.execute(text("DELETE FROM station"))

        # db.commit()

        logger.info("Tables vidées")

# Import du fichier stations.csv
        logger.info(f"Stations lues : {len(stations)}")

        stations_vues = set()
        stations_connues = set()
        
        nb_stations_inserees = 0
        nb_stations_rejetees = 0
        nb_stations_doublons = 0

        # for ligne in stations.to_dict("records"):
        for numero_ligne, ligne in enumerate(
            stations.to_dict("records"),
            start=2
        ):
            # identifiant_dupliqué
            if ligne["station_id"] in stations_vues:

                ajouter_anomalie(
                    rejets,
                    fichier="stations.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["station_id"],
                    colonne="station_id",
                    valeur=ligne["station_id"],
                    motif="identifiant dupliqué",
                    decision="rejet",
                    categorie="doublon"
                )

                nb_stations_rejetees += 1
                nb_stations_doublons += 1
                continue

            # capacité non positive         
            if ligne["capacite"] <= 0:

                ajouter_anomalie(
                    rejets,
                    fichier="stations.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["station_id"],
                    colonne="capacite",
                    valeur=ligne["capacite"],
                    motif="capacité non positive",
                    decision="rejet"
                )

                nb_stations_rejetees += 1
                continue
            # nom obligatoire
            if pd.isna(ligne["nom"]) or str(ligne["nom"]).strip() == "":

                ajouter_anomalie(
                    rejets,
                    fichier="stations.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["station_id"],
                    colonne="nom",
                    valeur=ligne["nom"],
                    motif="nom obligatoire",
                    decision="rejet"
                )

                nb_stations_rejetees += 1
                continue

            # commune obligatoire
            if pd.isna(ligne["commune"]) or str(ligne["commune"]).strip() == "":

                ajouter_anomalie(
                    rejets,
                    fichier="stations.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["station_id"],
                    colonne="commune",
                    valeur=ligne["commune"],
                    motif="commune obligatoire",
                    decision="rejet"
                )

                nb_stations_rejetees += 1
                continue

            station = Station(
                station_id=ligne["station_id"],
                nom=ligne["nom"],
                commune=ligne["commune"],
                capacite=ligne["capacite"],
                latitude=ligne["latitude"],
                longitude=ligne["longitude"],
                date_mise_en_service=ligne["date_mise_en_service"],
            )

            db.add(station)
            stations_vues.add(ligne["station_id"])
            stations_connues.add(ligne["station_id"])
               
            nb_stations_inserees += 1     
        # db.commit()

        logger.info("Import stations terminé")

        statistiques.append({
                "table": "station",
                "lues": len(stations),
                "inserees": nb_stations_inserees,
                "rejetees": nb_stations_rejetees,
                "doublons": nb_stations_doublons,
                "duree": 0,
})

        # stations_connues = set(stations["station_id"])

# Import du fichier trajets.csv
        logger.info(f"Trajets lues : {len(trajets)}")

        trajets_vus = set()

        nb_trajets_inseres = 0
        nb_trajets_rejetes = 0
        nb_trajets_doublons = 0

        # for ligne in trajets.to_dict("records"):
        for numero_ligne, ligne in enumerate(
                trajets.to_dict("records"),
                start=2
        ):

            if ligne["trajet_id"] in trajets_vus:
                logger.warning(
                    "REJET trajet %s : identifiant dupliqué",
                    ligne["trajet_id"]
                )
                # rejet = {
                #     "table": "trajet",
                #     "trajet_id": ligne["trajet_id"],
                #     "motif_rejet": "identifiant dupliqué"
                # }
                # rejets.append(rejet)
                ajouter_anomalie(
                    rejets,
                    fichier="trajets.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["trajet_id"],
                    colonne="trajet_id",
                    valeur=ligne["trajet_id"],
                    motif="identifiant dupliqué",
                    decision="rejet",
                    categorie="doublon"
                )
                nb_trajets_rejetes += 1
                nb_trajets_doublons += 1
                continue

                
            trajets_vus.add(
              ligne["trajet_id"]
            )

            valide, motif = duree_valide(
                ligne["duree_secondes"]
            )

            if not valide:
                logger.warning(
                    "REJET trajet %s : %s",
                    ligne["trajet_id"],
                    motif
                )

                # rejets.append({
                #     "table": "trajet",
                #     "trajet_id": ligne["trajet_id"],
                #     "motif_rejet": motif
                #     })

                ajouter_anomalie(
                    rejets,
                    fichier="trajets.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["trajet_id"],
                    colonne="duree_secondes",
                    valeur=ligne["duree_secondes"],
                    motif=motif,
                    decision="rejet"
                )
                nb_trajets_rejetes += 1
                continue


            valide, motif = station_referencee(
                ligne["station_depart"],
                stations_connues
            )

            if not valide:
                logger.warning(
                    "REJET trajet %s : %s",
                    ligne["trajet_id"],
                    motif
                )
                # rejets.append({
                #     "table": "trajet",
                #     "trajet_id": ligne["trajet_id"],
                #     "motif_rejet": motif
                #     })

                ajouter_anomalie(
                    rejets,
                    fichier="trajets.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["trajet_id"],
                    colonne="station_depart",
                    valeur=ligne["station_depart"],
                    motif=motif,
                    decision="rejet"
                )
                nb_trajets_rejetes += 1
                continue

            if pd.notna(ligne["station_arrivee"]):

                valide, motif = station_referencee(
                ligne["station_arrivee"],
                stations_connues
    )

                if not valide:
                  logger.warning(
                    "REJET trajet %s : %s",
                    ligne["trajet_id"],
                    motif
                  )
                  ajouter_anomalie(
                      rejets,
                      fichier="trajets.csv",
                      ligne=numero_ligne,
                      identifiant=ligne["trajet_id"],
                      colonne="station_arrivee",
                      valeur=ligne["station_arrivee"],
                      motif=motif,
                      decision="rejet"
                  )
                  nb_trajets_rejetes += 1
                  continue

            trajet = Trajet(
                trajet_id=ligne["trajet_id"],
                velo_id=ligne["velo_id"],
                depart_horodatage=ligne["depart_horodatage"],
                station_depart=ligne["station_depart"],
                station_arrivee=(None
                                 if pd.isna(ligne["station_arrivee"])
                                 else ligne["station_arrivee"]),
                duree_secondes=ligne["duree_secondes"],
                type_usager=ligne["type_usager"],
                usager_ref=(None 
                            if pd.isna(ligne["usager_ref"])
                            else ligne["usager_ref"]),
            )

            db.add(trajet)
            nb_trajets_inseres += 1

        # db.commit()

        logger.info("Import trajets terminé")

        statistiques.append({
                 "table": "trajet",
                 "lues": len(trajets),
                 "inserees": nb_trajets_inseres,
                 "rejetees": nb_trajets_rejetes,
                 "doublons": nb_trajets_doublons,
                 "duree": 0,
            })

# Import du fichier incidents.csv

        logger.info(f"Incidents lus : {len(incidents)}")

        incidents_vus = set()

        nb_incidents_inseres = 0
        nb_incidents_rejetes = 0
        nb_incidents_doublons = 0

        # for ligne in incidents.to_dict("records"):
        for numero_ligne, ligne in enumerate(
                incidents.to_dict("records"),
                start=2
        ):           
            if ligne["incident_id"] in incidents_vus:

                ajouter_anomalie(
                    rejets,
                    fichier="incidents.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["incident_id"],
                    colonne="incident_id",
                    valeur=ligne["incident_id"],
                    motif="identifiant dupliqué",
                    decision="rejet",
                    categorie="doublon"
                )

                nb_incidents_rejetes += 1
                nb_incidents_doublons += 1
                continue

            incidents_vus.add(ligne["incident_id"])

            incident = Incident(
               incident_id=ligne["incident_id"],
               date_signalement=ligne["date_signalement"],
               cible=ligne["cible"],
                velo_id=(None
                        if pd.isna(ligne["velo_id"])
                        else ligne["velo_id"]
                        ),
                station_id=(None
                            if pd.isna(ligne["station_id"])
                            else ligne["station_id"]
                            ),
                type_incident=ligne["type_incident"],
                statut=normaliser_statut(ligne["statut"]),
                date_resolution=(None
                                if pd.isna(ligne["date_resolution"])
                                else ligne["date_resolution"]
                                ),
                technicien=(None
                            if pd.isna(ligne["technicien"])
                            else ligne["technicien"]
                            ),  
                )

            db.add(incident)
            nb_incidents_inseres += 1

        db.commit()

        logger.info("Import incidents terminé")

        statistiques.append({
                "table": "incident",
                "lues": len(incidents),
                "inserees": nb_incidents_inseres,
                "rejetees": nb_incidents_rejetes,
                "doublons": nb_incidents_doublons,
                "duree": 0,
            })

    finally:
        db.close()

    # raise NotImplementedError("À compléter")
    ecrire_rejets(rejets)
    
    duree_globale = time.perf_counter() - debut_global
    
    logger.info("=== Récapitulatif ===")
    
    for statistique in statistiques:
        logger.info(
            "%s : lues=%d, insérées=%d, rejetées=%d, doublons=%d, durée=%.3f s",
            statistique["table"],
            statistique["lues"],
            statistique["inserees"],
            statistique["rejetees"],
            statistique["doublons"],
            statistique["duree"],
         )
    
    logger.info(
        "Total : lues=%d | insérées=%d | rejetées=%d | doublons=%d | durée=%.3f s" ,
        sum(s["lues"] for s in statistiques),
        sum(s["inserees"] for s in statistiques),
        sum(s["rejetees"] for s in statistiques),
        sum(s["doublons"] for s in statistiques),
        duree_globale,
    )
    
    if rejets:
        logger.warning(
            "%d ligne(s) rejetée(s). Voir %s.",
            len(rejets),
            FICHIER_REJETS,
        )
    else:
        logger.info("Aucun rejet de chargement.")


if __name__ == "__main__":
    main()
