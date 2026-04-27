import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURATION ---
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQOAWZCJ-vMQ"
CHAT_ID = "7836102896"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def detect_fvg(df):
    if len(df) < 3: return None
    b1, b2, b3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    if b3['Low'] > b1['High']:
        return {"type": "BULLISH", "gap": b3['Low'] - b1['High']}
    elif b3['High'] < b1['Low']:
        return {"type": "BEARISH", "gap": b1['Low'] - b3['High']}
    return None

# --- INTERFACE ---
st.set_page_config(page_title="Alpha Scanner", layout="wide")
st.title("🛡️ Alpha Quant Scanner")

st.sidebar.title("Contrôle")
ticker = st.sidebar.text_input("Ticker", "^IXIC")
btn = st.sidebar.button("Lancer le Scan")

if btn:
    data = yf.download(ticker, period="1d", interval="5m")
    if not data.empty:
        current_price = data['Close'].iloc[-1]
        fvg = detect_fvg(data)
        
        st.metric("Prix actuel Nasdaq", f"{current_price:.2f} $")
        
        if fvg:
            st.success(f"🔥 FVG {fvg['type']} DÉTECTÉ")
            msg = f"🎯 *SIGNAL IA*\nType: {fvg['type']}\nPrix: {current_price:.2f}"
            send_telegram(msg)
            st.toast("Telegram envoyé !")
        else:
            st.info("Aucun FVG détecté pour le moment.")
    else:
        st.error("Erreur de données.")
