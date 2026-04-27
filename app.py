import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta  # Pour les calculs techniques
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

st.title("🛡️ ALPHA SNIPER NQ - Intelligence Artificielle")
st.caption(f"Scan en cours... Dernière MAJ : {datetime.now().strftime('%H:%M:%S')}")

# Paramètres (comme dans ton Pine Script)
ticker = "NQ=F"
vol_target = 1.5
look_back = 20

try:
    df = yf.download(ticker, period="2d", interval="5m") # 5m est idéal pour cette stratégie
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # --- CALCULS ALPHA SNIPER ---
        # 1. Tendance (EMA 200)
        df['ema200'] = ta.ema(df['Close'], length=200)
        is_bull = df['Close'].iloc[-1] > df['ema200'].iloc[-1]
        is_bear = df['Close'].iloc[-1] < df['ema200'].iloc[-1]

        # 2. Volume
        v_ma = df['Volume'].rolling(20).mean()
        v_high = df['Volume'].iloc[-1] > (v_ma.iloc[-1] * vol_target)

        # 3. Liquidité (Sweep)
        h_max = df['High'].shift(1).rolling(look_back).max()
        l_min = df['Low'].shift(1).rolling(look_back).min()
        s_low = (df['Low'].iloc[-1] < l_min.iloc[-1]) and (df['Close'].iloc[-1] > l_min.iloc[-1])
        s_high = (df['High'].iloc[-1] > h_max.iloc[-1]) and (df['Close'].iloc[-1] < h_max.iloc[-1])

        # 4. Rejet (Mèches)
        total_range = df['High'] - df['Low']
        wick_down = df[['Open', 'Close']].min(axis=1) - df['Low']
        wick_up = df['High'] - df['Open', 'Close'].max(axis=1)
        rej_bull = wick_down.iloc[-1] > (total_range.iloc[-1] * 0.25)
        rej_bear = wick_up.iloc[-1] > (total_range.iloc[-1] * 0.25)

        # --- DÉTECTION DES SIGNAUX ---
        buy_signal = is_bull and s_low and v_high and rej_bull
        sell_signal = is_bear and s_high and v_high and rej_bear

        # --- INTERFACE ---
        col1, col2 = st.columns(2)
        current_price = float(df['Close'].iloc[-1])
        col1.metric("PRIX NASDAQ", f"{current_price:.2f} $")
        
        status = "RECHERCHE DE SIGNAL..."
        if buy_signal: status = "🔥 SIGNAL BUY DÉTECTÉ !"
        if sell_signal: status = "📉 SIGNAL SELL DÉTECTÉ !"
        col2.subheader(status)

        # --- ENVOI TELEGRAM ---
        if buy_signal or sell_signal:
            side = "BUY 🟢" if buy_signal else "SELL 🔴"
            alert_id = f"{side}_{current_price}"
            
            if 'last_alpha_alert' not in st.session_state or st.session_state.last_alpha_alert != alert_id:
                msg = (f"🎯 *ALPHA SNIPER SIGNAL*\n\n"
                       f"*Action:* {side}\n"
                       f"*Prix:* {current_price:.2f}\n"
                       f"*Volume:* {'Anormal' if v_high else 'Normal'}\n"
                       f"*Sweep:* {'Validé ✅'}\n"
                       f"⚠️ Vérifiez votre graphique !")
                send_telegram(msg)
                st.session_state.last_alpha_alert = alert_id
                st.balloons()

        st.line_chart(df[['Close', 'ema200']].tail(50))

except Exception as e:
    st.error(f"Erreur : {e}")
