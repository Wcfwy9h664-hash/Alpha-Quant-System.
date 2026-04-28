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
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except:
        pass

st.set_page_config(page_title="ALPHA SNIPER PRO", layout="wide")
st_autorefresh(interval=60000, key="bot_final")

st.title("🛡️ ALPHA SNIPER - PROP FIRM EDITION")
st.caption(f"Scan en cours... {datetime.now().strftime('%H:%M:%S')}")

ticker = "NQ=F"
look_back = 20
vol_target = 1.5

try:
    df = yf.download(ticker, period="5d", interval="5m")
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 1. RANGE TOKYO (00:00 - 08:00 UTC)
        df.index = pd.to_datetime(df.index)
        today_data = df.loc[df.index[-1].strftime('%Y-%m-%d')]
        tokyo = today_data.between_time('00:00', '08:00')
        t_high = float(tokyo['High'].max()) if not tokyo.empty else 999999
        t_low = float(tokyo['Low'].min()) if not tokyo.empty else 0

        # 2. INDICATEURS
        df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
        v_ma = df['Volume'].rolling(20).mean()
        h_max_lb = df['High'].shift(1).rolling(look_back).max()
        l_min_lb = df['Low'].shift(1).rolling(look_back).min()

        # 3. VALEURS ACTUELLES
        c_price = float(df['Close'].iloc[-1])
        c_high = float(df['High'].iloc[-1])
        c_low = float(df['Low'].iloc[-1])
        c_vol = float(df['Volume'].iloc[-1])
        c_ema = float(df['ema200'].iloc[-1])
        
        # 4. LOGIQUE SIGNAL
        v_high = c_vol > (v_ma.iloc[-1] * vol_target)
        s_low = (c_low < l_min_lb.iloc[-1]) and (c_price > l_min_lb.iloc[-1])
        s_high = (c_high > h_max_lb.iloc[-1]) and (c_price < h_max_lb.iloc[-1])
        
        buy_ok = (c_price > c_ema) and s_low and v_high and (c_price > t_high)
        sell_ok = (c_price < c_ema) and s_high and v_high and (c_price < t_low)

        # --- DASHBOARD ---
        c1, c2, c3 = st.columns(3)
        c1.metric("PRIX NQ", f"{c_price:.2f}")
        c2.metric("TOKYO HIGH", f"{t_high:.2f}")
        c3.metric("TOKYO LOW", f"{t_low:.2f}")

        # --- CALCULS SL / TP (RR 2) ---
        if buy_ok or sell_ok:
            # Calcul du risque basé sur le dernier plus bas/haut du sweep
            if buy_ok:
                sl = l_min_lb.iloc[-1] - 5 # 5 points de marge
                dist = c_price - sl
                tp = c_price + (dist * 2)
                side = "BUY 🟢"
            else:
                sl = h_max_lb.iloc[-1] + 5
                dist = sl - c_price
                tp = c_price - (dist * 2)
                side = "SELL 🔴"

            # ALERTES
            msg = (f"🎯 *ALPHA SIGNAL DETECTED*\n\n"
                   f"*Type:* {side}\n"
                   f"*Entrée:* {c_price:.2f}\n"
                   f"➖➖➖➖➖➖\n"
                   f"🚫 *STOP LOSS:* {sl:.2f}\n"
                   f"✅ *TAKE PROFIT (RR2):* {tp:.2f}\n"
                   f"➖➖➖➖➖➖\n"
                   f"💰 *Objectif:* {dist*20 if 'MNQ' in ticker else dist*2:.0f}$ (Approx)")
            
            if 'last_p' not in st.session_state or st.session_state.last_p != f"{side}_{c_price}":
                send_telegram(msg)
                st.session_state.last_p = f"{side}_{c_price}"
                st.balloons() if buy_ok else st.snow()

        st.line_chart(df[['Close', 'ema200']].tail(50))

except Exception as e:
    st.error(f"Erreur: {e}")
