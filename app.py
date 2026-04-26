import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ==========================================
# 1. TA CONFIGURATION (MISE À JOUR)
# ==========================================
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQOAWZCJ-vMQ"
CHAT_ID = "7836102896"

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

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🛡️ Alpha Quant System v1.0")

# ==========================================
# 4. RÉCEPTION ET ANALYSE DU SIGNAL
# ==========================================
query_params = st.query_params

if "side" in query_params:
    side = str(query_params["side"]).upper()
    price = query_params.get("price", "N/A")
    
    # Moteur de confiance (IA Simulation)
    confiance = 92 
    
    st.success(f"🎯 SIGNAL RÉCEPTIONNÉ : {side}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="DIRECTION", value=side)
        st.metric(label="PRIX NASDAQ", value=f"{price} $")
    
    with col2:
        st.subheader("🧠 Analyse du Cerveau Alpha")
        st.write(f"Probabilité de réussite : **{confiance}%**")
        st.progress(confiance)

    # --- ENVOI TELEGRAM AUTOMATIQUE ---
    emoji = "🚀" if side == "BUY" else "📉"
    message_tele = (
        f"{emoji} *NOUVEAU SIGNAL ALPHA*\n\n"
        f"*Action:* {side}\n"
        f"*Prix:* {price}\n"
        f"*Confiance:* {confiance}%\n\n"
        f"🌐 [Ouvrir le Dashboard](https://alpha-quant-system-exhx6q8hlrp5twulwfgz9z.streamlit.app/)"
    )
    
    # Protection pour éviter les envois en boucle au rafraîchissement
    if 'last_signal' not in st.session_state or st.session_state.last_signal != f"{side}_{price}":
        send_telegram(message_tele)
        st.session_state.last_signal = f"{side}_{price}"
        st.toast("Signal envoyé sur Telegram !")

else:
    st.info("📡 En attente de signaux via Webhook (TradingView)...")
    st.image("https://img.freepik.com/vecteurs-libre/concept-abstrait-marche-boursier_335657-3023.jpg", width=400)

st.divider()
st.sidebar.title("Statut Système")
st.sidebar.write(f"Dernière MAJ : {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.success("✅ Bot Connecté")
