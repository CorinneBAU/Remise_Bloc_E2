"""Écran Incidents.

À compléter : tableau filtrable par statut ; pour le rôle exploitant, changement de
statut d'un incident via l'API.
"""
import pandas as pd
import streamlit as st

from api_client import lister_incidents

st.title("Incidents")

reponse = lister_incidents()
incidents = reponse["resultats"]

st.write(
    f"{reponse['total']} incidents"
)

st.dataframe(
    pd.DataFrame(incidents),
    use_container_width=True,
)