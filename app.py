import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQOAWZCJ-vMQ"
CHAT_ID = "7836102896"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})

st.set_page_config(page_title="ALPHA SNIPER BOT", layout="wide")
st_autorefresh(interval=60000, key="bot_refresh")

st.title("🛡️ ALPHA SNIPER NQ")
st.caption(f"Scan auto actif • {datetime.now().strftime('%H:%M:%S')}")

ticker = "NQ=F"
vol_target = 1.5
look_back = 20

try:
    df = yf.download(ticker, period="2d", interval="5m")
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # --- CALCULS ALPHA (Version stable) ---
        # 1. EMA 200 (Calcul manuel pour éviter les bugs d'installation)
        df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # 2. Volume
        v_ma = df['Volume'].rolling(20).mean()
        
        # 3. Liquidité
        h_max = df['High'].shift(1).rolling(look_back).max()
        l_min = df['Low'].shift(1).rolling(look_back).min()

        # Dernières valeurs pour le signal
        c_price = float(df['Close'].iloc[-1])
        c_high = float(df['High'].iloc[-1])
        c_low = float(df['Low'].iloc[-1])
        c_vol = float(df['Volume'].iloc[-1])
        c_ema = float(df['ema200'].iloc[-1])
        
        # Logique des mèches (Rejet)
        range_bar = c_high - c_low
        body_min = min(float(df['Open'].iloc[-1]), c_price)
        body_max = max(float(df['Open'].iloc[-1]), c_price)
        wick_down = body_min - c_low
        wick_up = c_high - body_max

        # --- CONDITIONS ---
        is_bull = c_price > c_ema
        is_bear = c_price < c_ema
        v_high = c_vol > (v_ma.iloc[-1] * vol_target)
        s_low = (c_low < l_min.iloc[-1]) and (c_price > l_min.iloc[-1])
        s_high = (c_high > h_max.iloc[-1]) and (c_price < h_max.iloc[-1])
        rej_bull = wick_down > (range_bar * 0.25)
        rej_bear = wick_up > (range_bar * 0.25)

        buy_signal = is_bull and s_low and v_high and rej_bull
        sell_signal = is_bear and s_high and v_high and rej_bear

        # --- AFFICHAGE ---
        col1, col2 = st.columns(2)
        col1.metric("PRIX NQ", f"{c_price:.2f} $")
        
        if buy_signal:
            st.success("🔥 SIGNAL BUY ALPHA !")
            msg = f"🎯 *ALPHA BUY*\n\n*Prix:* {c_price:.2f}\n*Tendance:* Haussière\n*Volume:* Boosté 🚀"
            send_telegram(msg)
        elif sell_signal:
            st.error("📉 SIGNAL SELL ALPHA !")
            msg = f"🎯 *ALPHA SELL*\n\n*Prix:* {c_price:.2f}\n*Tendance:* Baissière\n*Volume:* Boosté 🚀"
            send_telegram(msg)
        else:
            col2.info("Analyse en cours : RAS")

        st.line_chart(df[['Close', 'ema200']].tail(50))

except Exception as e:
    st.error(f"En attente de connexion flux : {e}")
