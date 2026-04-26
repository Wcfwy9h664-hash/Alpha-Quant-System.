import streamlit as st
import requests
from datetime import datetime

# CONFIGURATION
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQOAWZCJ-vMQ"
CHAT_ID = "7836102896"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except:
        pass

st.title("🛡️ Alpha Quant System")

# Récupération des paramètres
query_params = st.query_params

if "side" in query_params:
    side = str(query_params["side"]).upper()
    price = query_params.get("price", "0")
    
    st.success(f"SIGNAL : {side} à {price}")
    
    msg = f"🚀 *SIGNAL ALPHA*\nDirection: {side}\nPrix: {price}"
    
    # Envoi unique
    if 'sent' not in st.session_state:
        send_telegram(msg)
        st.session_state['sent'] = True
        st.write("✅ Notifié sur Telegram")
else:
    st.info("En attente de signal...")

st.sidebar.write(f"Connecté : {datetime.now().strftime('%H:%M')}")
