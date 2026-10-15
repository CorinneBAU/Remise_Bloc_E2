"""Écran Stations.

À compléter : tableau des stations filtrable par commune, pagination.
"""
import pandas as pd
import streamlit as st

from api_client import lister_stations

st.title("Stations")

stations = lister_stations()

st.dataframe(
    pd.DataFrame(stations),
    use_container_width=True,
)