import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# CONFIGURATION
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQOAWZCJ-vMQ"
CHAT_ID = "7836102896"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})

def detect_fvg(df):
    if len(df) < 3: return None
    # Extraction propre des valeurs
    try:
        b1_high = float(df['High'].iloc[-3])
        b1_low = float(df['Low'].iloc[-3])
        b3_high = float(df['High'].iloc[-1])
        b3_low = float(df['Low'].iloc[-1])
        
        if b3_low > b1_high:
            return {"type": "BULLISH", "gap": b3_low - b1_high}
        elif b3_high < b1_low:
            return {"type": "BEARISH", "gap": b1_low - b3_high}
    except:
        pass
    return None

st.set_page_config(page_title="Alpha Quant Scanner", page_icon="🛡️")
st.title("🛡️ Alpha Quant Scanner")

# Barre latérale
ticker = st.sidebar.text_input("Symbole (Ex: NQ=F, BTC-USD, AAPL)", "NQ=F")
interval = st.sidebar.selectbox("UT", ["1m", "5m", "15m", "1h"], index=1)

if st.sidebar.button("Lancer le Scan"):
    try:
        # Téléchargement
        df = yf.download(ticker, period="1d", interval=interval)
        
        if df.empty:
            st.error(f"Aucune donnée pour {ticker}.")
        else:
            # NETTOYAGE DES COLONNES (Anti-erreur Series)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Récupération du prix
            current_price = float(df['Close'].iloc[-1])
            
            st.metric(f"Prix {ticker}", f"{current_price:.2f} $")
            st.line_chart(df['Close'])
            
            fvg = detect_fvg(df)
            if fvg:
                st.success(f"🔥 FVG {fvg['type']} détecté !")
                msg = f"🎯 *SIGNAL {fvg['type']}*\nSymbole: {ticker}\nPrix: {current_price:.2f}"
                send_telegram(msg)
            else:
                st.info("RAS : Pas de FVG sur les 3 dernières bougies.")
                
    except Exception as e:
        st.error(f"Erreur technique : {e}")

st.sidebar.divider()
st.sidebar.caption("En cas de bug, clique sur Reboot dans 'Manage App'")
