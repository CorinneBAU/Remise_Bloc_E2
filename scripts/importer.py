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
from api.services.fiabilisation import capacite_valide, date_coherente, normaliser_horodatage, normaliser_velo_id, station_referencee, duree_valide, normaliser_statut, statut_valide
from sqlalchemy import text


FICHIER_INCIDENTS = "./data/incidents.csv"
FICHIER_STATIONS = "./data/stations.csv"
FICHIER_TRAJETS = "./data/trajets.csv"

FICHIER_REJETS = "sorties/journal_chargement.csv"



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# Ecrire le ficher des rejets et des normalisations
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

#  Alimenter le journal des anomalies
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

    journal_anomalies: list[dict[str, Any]] = []
    statistiques: list[dict[str, Any]] = []

    logger.info("=== Début du chargement veloville ===")    

    stations = pd.read_csv(FICHIER_STATIONS)
    trajets = pd.read_csv(FICHIER_TRAJETS)
    incidents = pd.read_csv(FICHIER_INCIDENTS)

    db = SessionLocal()

    try:
        db.execute(text("DELETE FROM trajet"))
        db.execute(text("DELETE FROM incident"))
        db.execute(text("DELETE FROM station"))
       

        logger.info("Tables vidées")

# Import du fichier stations.csv
        logger.info(f"Stations lues : {len(stations)}")

        stations_vues = set()
        stations_connues = set()
        
        nb_stations_inserees = 0
        nb_stations_rejetees = 0
        nb_stations_doublons = 0

        for numero_ligne, ligne in enumerate(
            stations.to_dict("records"),
            start=2
        ):
            # identifiant_dupliqué
            if ligne["station_id"] in stations_vues:

                ajouter_anomalie(
                    journal_anomalies,
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
            valide, motif = capacite_valide(
                    ligne["capacite"])

            if not valide:
                ajouter_anomalie(
                    journal_anomalies,
                    fichier="stations.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["station_id"],
                    colonne="capacite",
                    valeur=ligne["capacite"],
                    motif=motif,
                    decision="rejet"
                )

                nb_stations_rejetees += 1
                continue
            # nom obligatoire
            if pd.isna(ligne["nom"]) or str(ligne["nom"]).strip() == "":

                ajouter_anomalie(
                    journal_anomalies,
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
                    journal_anomalies,
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
       

        logger.info("Import stations terminé")
        db.flush()
 
        statistiques.append({
                "table": "station",
                "lues": len(stations),
                "inserees": nb_stations_inserees,
                "rejetees": nb_stations_rejetees,
                "doublons": nb_stations_doublons,
                "duree": 0,
            })

       
# Import du fichier trajets.csv
        logger.info(f"Trajets lues : {len(trajets)}")

        trajets_vus = set()

        nb_trajets_inseres = 0
        nb_trajets_rejetes = 0
        nb_trajets_doublons = 0

        for numero_ligne, ligne in enumerate(
                trajets.to_dict("records"),
                start=2
            ):

            if ligne["trajet_id"] in trajets_vus:            
                ajouter_anomalie(
                    journal_anomalies,
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

            velo_id_normalise = normaliser_velo_id(
                    ligne["velo_id"]
                )

            if velo_id_normalise != ligne["velo_id"]:
                ajouter_anomalie(
                    journal_anomalies,
                    fichier="trajets.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["trajet_id"],
                    colonne="velo_id",
                    valeur=ligne["velo_id"],
                    motif="normalisation velo_id",
                    decision="normalisation"
                )

            depart_normalise = normaliser_horodatage(
                ligne["depart_horodatage"]
            )

            valide, motif = duree_valide(
                ligne["duree_secondes"]
            )

            if pd.isna(depart_normalise):
                ajouter_anomalie(
                    journal_anomalies,
                    fichier="trajets.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["trajet_id"],
                    colonne="depart_horodatage",
                    valeur=ligne["depart_horodatage"],
                    motif="horodatage invalide",
                    decision="rejet"
                )

                nb_trajets_rejetes += 1
                continue

            if not valide:            
                ajouter_anomalie(
                    journal_anomalies,
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
                ajouter_anomalie(
                    journal_anomalies,
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
                  ajouter_anomalie(
                      journal_anomalies,
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

            if (
                ligne["type_usager"] == "abonne"
                and pd.isna(ligne["usager_ref"])
            ):
                ajouter_anomalie(
                    journal_anomalies,
                    fichier="trajets.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["trajet_id"],
                    colonne="usager_ref",
                    valeur=ligne["usager_ref"],
                    motif="abonne sans usager_ref",
                    decision="rejet"
                )

                nb_trajets_rejetes += 1
                continue

            if (
                ligne["type_usager"] == "occasionnel"
                and pd.notna(ligne["usager_ref"])
            ):
                ajouter_anomalie(
                    journal_anomalies,
                    fichier="trajets.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["trajet_id"],
                    colonne="usager_ref",
                    valeur=ligne["usager_ref"],
                    motif="occasionnel avec usager_ref",
                    decision="rejet"
                )

                nb_trajets_rejetes += 1
                continue


            if ligne["type_usager"] not in {
                    "abonne",
                    "occasionnel"
                }:
                    ajouter_anomalie(
                        journal_anomalies,
                        fichier="trajets.csv",
                        ligne=numero_ligne,
                        identifiant=ligne["trajet_id"],
                        colonne="type_usager",
                        valeur=ligne["type_usager"],
                        motif="type_usager invalide",
                        decision="rejet"
                    )

                    nb_trajets_rejetes += 1
                    continue
                
            trajet = Trajet(
                trajet_id=ligne["trajet_id"],
                velo_id=velo_id_normalise,
                depart_horodatage=depart_normalise,
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

      
        logger.info("Import trajets terminé")
        db.flush()

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

        for numero_ligne, ligne in enumerate(
                incidents.to_dict("records"),
                start=2
            ):           
            if ligne["incident_id"] in incidents_vus:

                ajouter_anomalie(
                    journal_anomalies,
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

            if ligne["cible"] not in {"velo", "station"}:
                ajouter_anomalie(
                    journal_anomalies,
                    fichier="incidents.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["incident_id"],
                    colonne="cible",
                    valeur=ligne["cible"],
                    motif="cible invalide",
                    decision="rejet"
                )

                nb_incidents_rejetes += 1
                continue

            if ligne["cible"] == "station":            
                if pd.isna(ligne["station_id"]):
                    ajouter_anomalie(
                        journal_anomalies,
                        fichier="incidents.csv",
                        ligne=numero_ligne,
                        identifiant=ligne["incident_id"],
                        colonne="station_id",
                        valeur=ligne["station_id"],
                        motif="station obligatoire pour cible station",
                        decision="rejet"
                    )

                    nb_incidents_rejetes += 1
                    continue

            if ligne["cible"] == "station":
                if pd.notna(ligne["velo_id"]):
                    ajouter_anomalie(  
                        journal_anomalies,
                        fichier="incidents.csv",
                        ligne=numero_ligne,
                        identifiant=ligne["incident_id"],
                        colonne="velo_id",
                        valeur=ligne["velo_id"],                                                  
                        motif="velo_id interdit pour cible station",
                        decision="rejet"
                    )
                    nb_incidents_rejetes += 1
                    continue

            if ligne["cible"] == "velo":
                if pd.isna(ligne["velo_id"]):
                    ajouter_anomalie(
                        journal_anomalies,
                        fichier="incidents.csv",
                        ligne=numero_ligne,
                        identifiant=ligne["incident_id"],
                        colonne="velo_id",
                        valeur=ligne["velo_id"],
                        motif="velo obligatoire pour cible velo",
                        decision="rejet"
                    )

                    nb_incidents_rejetes += 1
                    continue

                if pd.notna(ligne["station_id"]):
                    ajouter_anomalie(
                        journal_anomalies,
                        fichier="incidents.csv",
                        ligne=numero_ligne,
                        identifiant=ligne["incident_id"],
                        colonne="station_id",
                        valeur=ligne["station_id"],
                        motif="station_id interdit pour cible velo",
                        decision="rejet"
                    )

                    nb_incidents_rejetes += 1
                    continue

            if pd.notna(ligne["station_id"]):
                valide, motif = station_referencee(
                    ligne["station_id"],
                    stations_connues
                    )
            
                if not valide:
                    ajouter_anomalie(
                        journal_anomalies,
                        fichier="incidents.csv",
                        ligne=numero_ligne,
                        identifiant=ligne["incident_id"],
                        colonne="station_id",
                        valeur=ligne["station_id"],
                        motif=motif,
                        decision="rejet"
                    )
                    nb_incidents_rejetes += 1
                    continue

            valide, motif = date_coherente(
                    pd.to_datetime(ligne["date_signalement"]),
                    pd.to_datetime(ligne["date_resolution"])
                    if pd.notna(ligne["date_resolution"])
                    else None
                )

            if not valide:              
                ajouter_anomalie(
                    journal_anomalies,
                    fichier="incidents.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["incident_id"],
                    colonne="date_resolution",
                    valeur=ligne["date_resolution"],
                    motif=motif,
                    decision="rejet"
                )

                nb_incidents_rejetes += 1
                continue

            statut_normalise = normaliser_statut(
                ligne["statut"]
            )
            if statut_normalise != ligne["statut"]:
                ajouter_anomalie(
                    journal_anomalies,
                    fichier="incidents.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["incident_id"],
                    colonne="statut",
                    valeur=ligne["statut"],
                    motif="normalisation statut",
                    decision="normalisation"
                )

            valide, motif = statut_valide(
                statut_normalise
            )

            if not valide:           
                ajouter_anomalie(
                    journal_anomalies,
                    fichier="incidents.csv",
                    ligne=numero_ligne,
                    identifiant=ligne["incident_id"],
                    colonne="statut",
                    valeur=ligne["statut"],
                    motif=motif,
                    decision="rejet"
                )

                nb_incidents_rejetes += 1
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
                statut=statut_normalise,
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



    ecrire_rejets(journal_anomalies)
    
    duree_globale = time.perf_counter() - debut_global
    
    logger.info("=== Récapitulatif ===")
    
    for statistique in statistiques:
        logger.info(
            "%s : lues=%d, insérées=%d, rejetées=%d (dont %d doublons), durée=%.3f s",
            statistique["table"],
            statistique["lues"],
            statistique["inserees"],
            statistique["rejetees"],
            statistique["doublons"],
            statistique["duree"],
         )
    
    logger.info(
        "Total : lues=%d | insérées=%d | rejetées=%d (dont %d doublons) | durée=%.3f s" ,
        sum(s["lues"] for s in statistiques),
        sum(s["inserees"] for s in statistiques),
        sum(s["rejetees"] for s in statistiques),
        sum(s["doublons"] for s in statistiques),
        duree_globale,
    )
    
    if journal_anomalies:

        nb_rejets = sum(
            1
            for ligne in journal_anomalies
            if ligne["decision"] == "rejet"
        )

        nb_normalisations = sum(
            1
            for ligne in journal_anomalies
            if ligne["decision"] == "normalisation"
        )

        logger.info(
            "Journal généré : %d rejets(s) et %d normalisation(s). Voir %s.",
            nb_rejets,
            nb_normalisations,
            FICHIER_REJETS,
        )
    else:
        logger.info("Aucun rejet de chargement.")


if __name__ == "__main__":
    main()
