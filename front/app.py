"""Page d'accueil Streamlit : connexion.

À compléter : formulaire identifiant / mot de passe, appel de POST /auth/login via
api_client, stockage du jeton et du rôle dans st.session_state,
message d'erreur en français en cas d'échec.

Lancement : streamlit run front/app.py
"""
import streamlit as st

st.set_page_config(
    page_title="VéloVille",
)

st.title("VéloVille")

st.write(
    "Application de consultation du réseau VéloVille"
)