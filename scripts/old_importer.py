"""Import et fiabilisation des trois exports CSV dans PostgreSQL.

À compléter : lire data/stations.csv, data/trajets.csv et data/incidents.csv,
appliquer les règles de fiabilisation (api/services/fiabilisation.py),
charger les lignes valides, journaliser les rejets et les avertissements.
Le script doit être idempotent : deux exécutions successives laissent la
base dans le même état.

Usage prévu : python scripts/importer.py [--dossier data]
"""
import pandas as pd
from api.database import SessionLocal
from api.models import Station, Trajet, Incident
from api.services.fiabilisation import station_referencee, duree_valide, normaliser_statut
from sqlalchemy import text


def main() -> None:
    stations = pd.read_csv("./data/stations.csv")
    trajets = pd.read_csv("./data/trajets.csv")
    incidents = pd.read_csv("./data/incidents.csv")

    db = SessionLocal()

    try:

        db.execute(text("DELETE FROM trajet"))
        db.execute(text("DELETE FROM incident"))
        db.execute(text("DELETE FROM station"))

        db.commit()

        print("Tables vidées")

# Import du fichier stations.csv
        print(f"Stations lues : {len(stations)}")

        for ligne in stations.to_dict("records"):

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

        db.commit()

        print("Import stations terminé")

        stations_connues = set(stations["station_id"])

# Import du fichier trajets.csv
        print(f"Trajets lues : {len(trajets)}")

        trajets_vus = set()
        
        for ligne in trajets.to_dict("records"):

            if ligne["trajet_id"] in trajets_vus:
                print(
                 f"REJET trajet {ligne['trajet_id']} : identifiant dupliqué"
                )
                continue

            trajets_vus.add(
              ligne["trajet_id"]
            )

            valide, motif = duree_valide(
                ligne["duree_secondes"]
            )

            if not valide:
                print(
                    f"REJET trajet {ligne['trajet_id']} : {motif}"
                )
                continue


            valide, motif = station_referencee(
                ligne["station_depart"],
                stations_connues
            )

            if not valide:
                print(
                  f"REJET trajet {ligne['trajet_id']} : {motif}"
                )
                continue

            if pd.notna(ligne["station_arrivee"]):

                valide, motif = station_referencee(
                ligne["station_arrivee"],
                stations_connues
    )

                if not valide:
                  print(
                  f"REJET trajet {ligne['trajet_id']} : {motif}"
                  )
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

        db.commit()

        print("Import trajets terminé")

# Import du fichier incidents.csv

        print(f"Incidents lus : {len(incidents)}")
        for ligne in incidents.to_dict("records"):

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

        db.commit()

        print("Import incidents terminé")

    finally:
        db.close()

    # raise NotImplementedError("À compléter")


if __name__ == "__main__":
    main()
