"""Écran Stations.

À compléter : tableau des stations filtrable par commune, pagination.
"""
import pandas as pd
import streamlit as st
import math

from api_client import lister_stations, ErreurApi

st.title("Stations")

@st.cache_data(ttl=3600)
def charger_communes():
    reponse = lister_stations(
        page=1,
        taille_page=100,
    )

    return ["Toutes"] + sorted(
        {
            station["commune"]
            for station in reponse["resultats"]
        }
    )

# ============================================================
# Filtres
# ============================================================

# commune = st.text_input(
#     "Commune"
# )

# Récupération d'une page pour alimenter la liste
# reponse_communes = lister_stations(
#     page=1,
#     taille_page=100,
# )

# communes = ["Toutes"] + sorted(
#     {
#         station["commune"]
#         for station in reponse_communes["resultats"]
#     }
# )
communes = charger_communes()

commune = st.selectbox(
    "Commune",
    communes,
)

commune_api = None

if commune != "Toutes":
    commune_api = commune

taille_page = st.selectbox(
    "Taille de page",
    [10, 20, 50],
    index=1,
)

page = st.number_input(
    "Page",
    min_value=1,
    value=1,
    step=1,
)

# ============================================================
# Chargement
# ============================================================

with st.spinner("Chargement des stations..."):
    try:
        reponse = lister_stations(
            commune=commune_api,
            page=page,
            taille_page=taille_page,
        )

    except ErreurApi as erreur:
        st.error(
            f"Impossible de récupérer les stations : {erreur}"
        )
        st.stop()

stations = reponse["resultats"]

# ============================================================
# État vide
# ============================================================

if not stations:
    st.info(
        "Aucune station à afficher."
    )
    st.stop()

# ============================================================
# Informations pagination
# ============================================================

total = reponse["total"]

nb_pages = math.ceil(
    total / taille_page
)

st.write(
    f"{total} stations au total"
)

st.caption(
    f"Page {page} sur {nb_pages}"
)

# ============================================================
# Tableau
# ============================================================

df = pd.DataFrame(stations)

colonnes = [
    "station_id",
    "nom",
    "commune",
    "capacite",
    "date_mise_en_service",
]

st.dataframe(
    df[colonnes],
    use_container_width=True,
)
