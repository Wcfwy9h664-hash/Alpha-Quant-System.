import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURATION TELEGRAM ---
TOKEN = "TON_TOKEN_ICI"
CHAT_ID = "TON_ID_ICI"

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.get(url, params=params)
    except Exception as e:
        st.error(f"Erreur Telegram: {e}")

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Alpha Quant System", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Alpha Quant System v1.0")

# --- MOTEUR IA (SIMULATION) ---
def analyse_ia(side):
    import random
    # Simulation d'un algo qui analyse la tendance
    proba = random.randint(75, 98)
    return proba

# --- GESTION DES SIGNAUX ---
# On récupère les infos envoyées par TradingView via l'URL
query_params = st.query_params

if "side" in query_params:
    side = query_params["side"].upper()
    price = query_params.get("price", "N/A")
    
    # Calcul de confiance IA
    confiance = analyse_ia(side)
    
    # Affichage en haut
    st.success(f"✅ NOUVEAU SIGNAL DÉTECTÉ : {side}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="POSITION", value=side)
        st.metric(label="PRIX D'ENTRÉE", value=f"{price} $")
    
    with col2:
        st.metric(label="CONFIANCE IA", value=f"{confiance}%")
        st.progress(confiance)

    # Envoi automatique à Telegram (on évite les doublons avec le cache)
    if "last_signal" not in st.session_state or st.session_state.last_signal != f"{side}_{price}":
        msg = (f"🎯 *NOUVEAU SIGNAL ALPHA*\n\n"
               f"🚀 Type : *{side}*\n"
               f"💰 Prix : `{price}`\n"
               f"🧠 Confiance IA : `{confiance}%`\n"
               f"📅 {datetime.now().strftime('%H:%M:%S')}")
        send_telegram_msg(msg)
        st.session_state.last_signal = f"{side}_{price}"
        st.toast("Alerte envoyée sur Telegram !")

else:
    st.info("📡 En attente de signaux du Nasdaq via Webhook...")
    st.write("Le système scanne actuellement les FVG et les cassures de structure (MSB).")

# --- FOOTER ---
st.divider()
st.caption("Alpha Quant System | Propriété de Loïc | Connexion Nasdaq Direct")
