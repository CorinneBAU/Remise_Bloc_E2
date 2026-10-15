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

st.subheader("Activité par jour")
st.dataframe(
    pd.DataFrame(
        activite_par_jour()
    ),
    use_container_width=True,
)

st.subheader("Stations actives")
st.dataframe(
    pd.DataFrame(
        stations_actives()
    ),
    use_container_width=True,
)

st.subheader("Incidents par statut")
st.dataframe(
    pd.DataFrame(
        incidents_par_statut()
    ),
    use_container_width=True,
)