import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# ==========================================
# 1. CONFIGURATION (TES INFOS)
# ==========================================
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQOAWZCJ-vMQ"
CHAT_ID = "7836102896"

# ==========================================
# 2. FONCTIONS TECHNIQUES
# ==========================================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def detect_fvg(df):
    """Détecte le dernier FVG sur les 3 dernières bougies"""
    # Un FVG haussier : Bas de la bougie 3 > Haut de la bougie 1
    # Un FVG baissier : Haut de la bougie 3 < Bas de la bougie 1
    last_fvg = None
    
    b1 = df.iloc[-3]
    b2 = df.iloc[-2]
    b3 = df.iloc[-1]
    
    if b3['Low'] > b1['High']:
        last_fvg = {"type": "BULLISH (Achat)", "gap": b3['Low'] - b1['High']}
    elif b3['High'] < b1['Low']:
        last_fvg = {"type": "BEARISH (Vente)", "gap": b1['Low'] - b3['High']}
        
    return last_fvg

# ==========================================
# 3. INTERFACE STREAMLIT
# ==========================================
st.set_page_config(page_title="Alpha Quant IA", layout="wide")
st.title("🛡️ Alpha Quant System - Scanner Autonome")

# Barre latérale pour le contrôle
st.sidebar.title("Paramètres du Bot")
ticker = st.sidebar.text_input("Symbole à scanner", "^IXIC") # ^IXIC = Nasdaq
interval = st.sidebar.selectbox("Unité de temps", ["1m", "5m", "15m", "1h"])

if st.sidebar.button("Lancer le Scan Manuel"):
    # Récupération des données
    data = yf.download(ticker, period="1d", interval=interval)
    
    if not data.empty:
        current_price = data['Close'].iloc[-1]
        fvg = detect_fvg(data)
        
        st.subheader(f"📊 Analyse en temps réel : {ticker}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Prix Actuel", f"{current_price:.2f} $")
            st.line_chart(data['Close'].tail(20))
            
        with col2:
            st.subheader("🧠 Cerveau Alpha")
            if fvg:
                confiance = 95
                st.success(f"🔥 FVG DÉTECTÉ : {fvg['type']}")
                st.write(f"Taille du déséquilibre : {fvg['gap']:.2f} pts")
                
                # Envoi Telegram
                msg = (f"🎯 *SIGNAL ALGO DÉTECTÉ*\n\n"
                       f"Marché: {ticker}\n"
                       f"Type: {fvg['type']}\n"
                       f"Prix: {current_price:.2f}\n"
                       f"Confiance: {confiance}%")
                send_telegram(msg)
                st.toast("Alerte envoyée !")
            else:
                confiance = 15
                st.info("⌛ Aucun déséquilibre (FVG) majeur détecté.")
            
            st.progress(confiance)
            st.write(f"Indice de confiance : {confiance}%")

    else:
        st.error("Impossible de récupérer les données du marché.")

st.divider()
st.caption("Le bot scanne automatiquement les Fair Value Gaps sans avoir besoin de TradingView Pro.")
