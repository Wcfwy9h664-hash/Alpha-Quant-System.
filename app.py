import streamlit as st
import requests
from datetime import datetime

# ==========================================
# 1. CONFIGURATION (TOKEN ET ID VÉRIFIÉS)
# ==========================================
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQOAWZCJ-vMQ"
CHAT_ID = "7836102896"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, data=payload)
        return r.json() # On récupère la réponse de Telegram
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ==========================================
# 2. INTERFACE
# ==========================================
st.set_page_config(page_title="Alpha Quant System", layout="wide")
st.title("🛡️ Alpha Quant System v1.0")

# Récupération des paramètres dans l'URL
params = st.query_params

if "side" in params:
    side = str(params["side"]).upper()
    price = params.get("price", "N/A")
    
    st.success(f"🎯 SIGNAL DÉTECTÉ : {side} à {price}")
    
    # Bouton de test manuel au cas où l'automatique rate
    if st.button("🚀 TESTER L'ENVOI MAINTENANT"):
        res = send_telegram(f"✅ TEST MANUEL\nDirection: {side}\nPrix: {price}")
        if res.get("ok"):
            st.balloons()
            st.success("Reçu sur Telegram !")
        else:
            st.error(f"Erreur Telegram : {res}")

    # Envoi auto (une seule fois par chargement)
    if 'sent' not in st.session_state:
        msg = f"🚀 *NOUVEAU SIGNAL*\n\n*Action:* {side}\n*Prix:* {price}"
        send_telegram(msg)
        st.session_state['sent'] = True
        st.info("Tentative d'envoi automatique effectuée.")

else:
    st.warning("📡 En attente de signal... (Utilisez le lien de test)")
    
    # SECTION DIAGNOSTIC (Pour toi)
    st.divider()
    st.subheader("🛠️ Diagnostic de connexion")
    if st.button("Vérifier mon Bot Telegram"):
        check = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe").json()
        if check.get("ok"):
            st.success(f"Le Bot est en ligne ! Nom : {check['result']['first_name']}")
        else:
            st.error("Le Token est invalide. Vérifiez GitHub.")
