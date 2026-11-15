"""Écran Indicateurs.

À compléter : trois st.metric et trois tableaux issus des trois endpoints
/indicateurs. Aucun graphique.
"""
import pandas as pd
import streamlit as st

from api_client import (
    activite_par_jour,
    stations_actives,
    incidents_par_statut,
)

st.title("Indicateurs")

# st.subheader("Activité par jour")
# st.dataframe(
#     pd.DataFrame(
#         activite_par_jour()
#     ),
#     use_container_width=True,
# )

# st.subheader("Stations actives")
# st.dataframe(
#     pd.DataFrame(
#         stations_actives()
#     ),
#     use_container_width=True,
# )

# st.subheader("Incidents par statut")
# st.dataframe(
#     pd.DataFrame(
#         incidents_par_statut()
#     ),
#     use_container_width=True,
# )

# ============================================================
# Activité par jour
# ============================================================

activite = activite_par_jour()

st.subheader("Activité par jour")

st.metric(
    "Nombre de jours",
    len(activite["donnees"]),
)

st.dataframe(
    pd.DataFrame(
        activite["donnees"]
    ),
    use_container_width=True,
)

# ============================================================
# Stations actives
# ============================================================

stations = stations_actives()

st.subheader("Stations actives")

st.metric(
    "Stations affichées",
    len(stations["donnees"]),
)

st.dataframe(
    pd.DataFrame(
        stations["donnees"]
    ),
    use_container_width=True,
)

# ============================================================
# Incidents par statut
# ============================================================

incidents = incidents_par_statut()

st.subheader("Incidents par statut")

st.metric(
    "Délai moyen de résolution (h)",
    incidents["delai_moyen_resolution_heures"],
)

st.dataframe(
    pd.DataFrame(
        incidents["donnees"]
    ),
    use_container_width=True,
)