import pandas as pd

#*************************************************************************
# Chargement des fichiers
#*************************************************************************

incidents = pd.read_csv("./data/incidents.csv")
stations = pd.read_csv("./data/stations.csv")
trajets = pd.read_csv("./data/trajets.csv")


#*************************************************************************
# 1ère analyse de base des fichiers
#*************************************************************************

print(f"structure fichiers INCIDENTS : ",incidents.shape)
incidents.info()
valeurs_statut = incidents["statut"].value_counts()
print(f"\nvaleurs_statut\n", valeurs_statut)

valeurs_cible = incidents["cible"].value_counts()
print(f"\nvaleurs_cible\n", valeurs_cible)

nb_doublons_incidents = incidents.duplicated().sum()
print(f"nb_doublons_incidents", nb_doublons_incidents)

print("=" * 60)
print(f"structure fichiers STATIONS : ",stations.shape)
stations.info()
nb_doublons_stations = stations.duplicated().sum()
print(f"nb_doublons_stations", nb_doublons_stations)

print("=" * 60)
print(f"structure fichiers TRAJETS : ", trajets.shape)
trajets.info()
nb_doublons_trajets = trajets.duplicated().sum()
print(f"nb_doublons_trajets", nb_doublons_trajets)


#*************************************************************************
# Fichier INCIDENTS
#*************************************************************************

print("\nAnalyses du fichier INCIDENTS")
# Vérifier l'unicité de incident_id
doublons_incidents_id = incidents["incident_id"].duplicated()
nb_doublons_incidents_id = doublons_incidents_id.sum()
print(f"nb_doublons_incidents_id : ",nb_doublons_incidents_id)

# Déterminer le nombre de 'statut' non écrit en minuscule et qui ne comporte pas "_"
casse_statut_correcte = incidents["statut"].str.lower().str.replace(" ","_")
comparatif_casse_statut = incidents["statut"] != casse_statut_correcte
nb_lignes_casse_statut_a_modifier = comparatif_casse_statut.sum()
print(f"nb_lignes_casse_statut_a_modifier : ",nb_lignes_casse_statut_a_modifier)

# Déterminer le nombre de lignes où date_résolution < date_signalement
incidents["date_resolution"] = pd.to_datetime(incidents["date_resolution"])
incidents["date_signalement"] = pd.to_datetime(incidents["date_signalement"])

dates_incoherentes = (incidents["date_resolution"] < incidents["date_signalement"])
nb_dates_incoherentes = dates_incoherentes.sum()
print(f"nb_lignes_dates_incoherentes : ",nb_dates_incoherentes)

# Déterminer le nombre de lignes dont la date_signalement ne respecte pas le format AAAA-MM-JJ HH:MM
# ==> aucune anomalie détectée
date_signalement_incorrecte = pd.to_datetime(
                                            incidents.loc[
                                                incidents["date_signalement"].notna(), 
                                                "date_signalement"
                                            ],
                                            format ="%Y-%m-%d %H:%M",
                                            errors="coerce"
                                            )
nb_date_signalement_incorrecte = date_signalement_incorrecte.isna().sum()
print(f"nb_lignes_date_signalement_incorrecte : ",nb_date_signalement_incorrecte)

# Déterminer le nombre de lignes dont la date_resolution ne respecte pas le format AAAA-MM-JJ HH:MM
# ==> aucune anomalie détectée
date_resolution_incorrecte = pd.to_datetime(
                                            incidents.loc[
                                                incidents["date_resolution"].notna(), 
                                                "date_resolution"
                                            ],
                                            format ="%Y-%m-%d %H:%M",
                                            errors="coerce"
                                            )
nb_date_resolution_incorrecte = date_resolution_incorrecte.isna().sum()
print(f"nb_lignes_date_resolution_incorrecte : ",nb_date_resolution_incorrecte)

# Déterminer le nombre de lignes dont la valeur dans station_id est inconnue dans le fichier stations.csv
station_id_inconnu = (~incidents["station_id"].isin(stations["station_id"]) & (incidents["station_id"].notna()))
nb_station_id_inconnu = station_id_inconnu.sum()
print(f"nb_station_id_inconnu : ",nb_station_id_inconnu)


#*************************************************************************
# Fichier TRAJETS
#*************************************************************************

print("\nAnalyses du fichier TRAJETS")
# Vérifier l'unicité de trajet_id
doublons_trajet_id = trajets["trajet_id"].duplicated()
nb_doublons_trajet_id = doublons_trajet_id.sum()
print(f"nb_doublons_trajet_id : ",nb_doublons_trajet_id)

# Déterminer le nombre trajets dont la durée est nulle ou négative
lignes_duree_secondes_incorrecte  = trajets["duree_secondes"] <= 0
nb_lignes_duree_secondes_incorrecte = lignes_duree_secondes_incorrecte.sum()
print(f"nb_lignes_duree_secondes_incorrecte : ",nb_lignes_duree_secondes_incorrecte)

# Déterminer le nombre de lignes dont la date ne respecte pas le format AAAA-MM-JJ HH:MM:SS
date_horodatage_incorrecte = pd.to_datetime(trajets["depart_horodatage"], 
                                            format ="%Y-%m-%d %H:%M:%S",
                                            errors="coerce")
nb_date_horodatage_incorrecte = date_horodatage_incorrecte.isna().sum()
print(f"nb_lignes_date_horodatage_incorrecte : ",nb_date_horodatage_incorrecte)

# Déterminer le nombre de lignes dont la valeur dans station_depart est inconnue dans le fichier stations.csv
station_depart_inconnue = ~trajets["station_depart"].isin(stations["station_id"])
nb_station_depart_inconnue = station_depart_inconnue.sum()
print(f"nb_station_depart_inconnue : ",nb_station_depart_inconnue)

# Déterminer le nombre de lignes dont la valeur dans station_arrivee est inconnue dans le fichier stations.csv
station_arrivee_inconnue = ~trajets["station_arrivee"].isin(stations["station_id"]) & (trajets["station_arrivee"].notna())
nb_station_arrivee_inconnue = station_arrivee_inconnue.sum()
print(f"nb_station_arrivee_inconnue : ",nb_station_arrivee_inconnue)

# Déterminer si les 12 doublons de lignes entières correspondent au 12 trajet_id non uniques
douze_doublons = trajets[trajets["trajet_id"].duplicated(keep=False)].sort_values("trajet_id")
print(f"\naffichage des douze_doublons\n",douze_doublons)

#*************************************************************************
# Fichier STATIONS
#*************************************************************************

print("\nAnalyses du fichier STATIONS")
# Vérifier l'unicité de station_id
doublons_station_id = stations["station_id"].duplicated()
nb_doublons_station_id = doublons_station_id.sum()
print(f"nb_doublons_station_id : ",nb_doublons_station_id)

# Déterminer le nombre de lignes dont la date ne respecte pas le format AAAA-MM-JJ
# ==> aucune anomalie détectée
date_mise_en_service_incorrecte = pd.to_datetime(stations["date_mise_en_service"], 
                                            format ="%Y-%m-%d",
                                            errors="coerce")
nb_date_mise_en_service_incorrecte = date_mise_en_service_incorrecte.isna().sum()
print(f"nb_date_mise_en_service_incorrecte : ",nb_date_mise_en_service_incorrecte)

