"""Page d'accueil Streamlit : connexion.

À compléter : formulaire identifiant / mot de passe, appel de POST /auth/login via
api_client, stockage du jeton et du rôle dans st.session_state,
message d'erreur en français en cas d'échec.

Lancement : streamlit run front/app.py
"""
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

st.set_page_config(
    page_title="VéloVille",
)

st.title("VéloVille")

st.write(
    "Application de consultation du réseau VéloVille"
)

if "token" not in st.session_state:
    st.session_state["token"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None

if not st.session_state["token"]:
    with st.form("connexion"):
        username = st.text_input(
            "Identifiant")
        password = st.text_input(
            "Mot de passe",
            type="password",)
        connexion = st.form_submit_button(
            "Se connecter")

    if connexion:
        try:    
            response = requests.post(
                f"{API_URL}/auth/login",
                json={
                "username": username,
                "password": password,
                },
                timeout=5,
                )
            
            response.raise_for_status()
            
            donnees = response.json()
            
            st.session_state["token"] = (
                donnees["access_token"]
                )
            
            st.session_state["role"] = (
                donnees["role"]
                )

            st.session_state["username"] = username
            
            st.success(
                f"Connecté en tant que {donnees['role']}"
                )
            
        except requests.HTTPError:    
            st.error(
            "Identifiant ou mot de passe incorrect."
            )
            
        except requests.RequestException:        
            st.error(
            "Impossible de joindre l'API VéloVille."
            )
        
if st.session_state["token"]:
    st.success(
        f"Connecté en tant que "
        f"{st.session_state['username']} "
        f"(rôle : {st.session_state['role']})."
    )

    st.info(
        "Utilisez le menu latéral pour accéder aux écrans."
    )

    if st.button("Se déconnecter"):

        st.session_state["token"] = None
        st.session_state["role"] = None
        st.session_state["username"] = None

        st.rerun()