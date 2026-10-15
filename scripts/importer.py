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
from api.models import Station

def main() -> None:
    stations = pd.read_csv("./data/stations.csv")
    # trajets = pd.read_csv("./data/trajets.csv")
    # incidents = pd.read_csv("./data/incidents.csv")

    db = SessionLocal()
    try:

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

    finally:
        db.close()

    # raise NotImplementedError("À compléter")


if __name__ == "__main__":
    main()
