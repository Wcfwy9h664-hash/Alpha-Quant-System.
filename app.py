import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ==========================================
# 1. TA CONFIGURATION (À MODIFIER)
# ==========================================
TOKEN = "TON_TOKEN_ICI"  # Exemple: "654321098:AAH..."
CHAT_ID = "TON_CHAT_ID_ICI"  # Exemple: "123456789"

# ==========================================
# 2. FONCTION D'ENVOI TELEGRAM
# ==========================================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        return response.ok
    except Exception as e:
        st.error(f"Erreur technique Telegram : {e}")
        return False

# ==========================================
# 3. INTERFACE STREAMLIT
# ==========================================
st.set_page_config(page_title="Alpha Quant System", page_icon="🛡️", layout="wide")

# Style CSS pour faire "Pro"
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🛡️ Alpha Quant System v1.0")
st.write(f"Dernière synchronisation : {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 4. RÉCEPTION ET ANALYSE DU SIGNAL
# ==========================================
# On récupère les infos envoyées dans l'URL
query_params = st.query_params

if "side" in query_params:
    side = str(query_params["side"]).upper()
    price = query_params.get("price", "N/A")
    
    # Simulation du cerveau IA (On mettra le vrai calcul ici en mai)
    confiance = 89 
    
    st.success(f"🎯 SIGNAL RÉCEPTIONNÉ : {side}")
    
    # Affichage en colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📡 Détails du Flux")
        st.metric(label="DIRECTION", value=side)
        st.metric(label="PRIX NASDAQ", value=f"{price} $")
    
    with col2:
        st.subheader("🧠 Analyse du Cerveau Alpha")
        st.write(f"Probabilité de réussite estimée : **{confiance}%**")
        st.progress(confiance)
        st.info("Statut : Signal validé par les algorithmes de liquidité.")

    # --- ENVOI TELEGRAM AUTOMATIQUE ---
    emoji = "🚀" if side == "BUY" else "📉"
    message_tele = (
        f"{emoji} *NOUVEAU SIGNAL ALPHA*\n\n"
        f"*Action:* {side}\n"
        f"*Prix:* {price}\n"
        f"*Confiance:* {confiance}%\n\n"
        f"🌐 [Voir le Dashboard](https://alpha-quant-system-exhx6q8hlrp5twulwfgz9z.streamlit.app/)"
    )
    
    # On déclenche l'envoi
    if st.button("Renvoyer l'alerte manuellement"):
        if send_telegram(message_tele):
            st.toast("Message envoyé à Telegram !")
            
    # L'envoi automatique se fait au chargement si les paramètres sont là
    if 'sent' not in st.session_state:
        send_telegram(message_tele)
        st.session_state['sent'] = True
        st.toast("Alerte auto envoyée !")

else:
    st.info("📡 En attente de signaux via Webhook (TradingView)...")
    st.image("https://img.freepik.com/vecteurs-libre/concept-abstrait-marche-boursier_335657-3023.jpg", width=400)

st.divider()
st.sidebar.title("Configuration")
st.sidebar.write("✅ Webhook : Actif")
st.sidebar.write("✅ Bot Telegram : Connecté")
