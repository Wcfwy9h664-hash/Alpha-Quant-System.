import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Alpha Quant System", layout="wide")

st.title("🛡️ Alpha Quant System v1.0")
st.sidebar.header("Paramètres Système")

# Simulation d'un moteur IA
def analyse_ia(price, side):
    # Ici, plus tard, on mettra le vrai cerveau
    # Pour l'instant, on simule une probabilité
    import random
    proba = random.randint(70, 95)
    return proba

# Interface principale
col1, col2 = st.columns(2)

with col1:
    st.subheader("📡 Flux de Signaux")
    if "side" in st.query_params:
        side = st.query_params["side"]
        price = st.query_params["price"]
        confiance = analyse_ia(price, side)
        
        st.metric(label=f"Signal {side.upper()}", value=f"{price} $", delta=f"Confiance: {confiance}%")
        st.write(f"Dernière alerte reçue à : {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.info("En attente de signaux du Nasdaq...")

with col2:
    st.subheader("🧠 Analyse du Cerveau Alpha")
    st.progress(85)
    st.write("Le système analyse les FVG et la liquidité en temps réel.")

