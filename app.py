import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, time
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. CONFIGURATION
# ==========================================
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQOAWZCJ-vMQ"
CHAT_ID = "7836102896"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except Exception as e:
        st.error(f"Erreur Telegram : {e}")

st.set_page_config(page_title="ALPHA SNIPER PRO", page_icon="🎯", layout="wide")
st_autorefresh(interval=60000, key="alpha_pro_refresh")

st.title("🎯 ALPHA SNIPER - Session Breakout")
st.caption(f"Scan Multi-Sessions • {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 2. CALCULS DES SESSIONS & INDICATEURS
# ==========================================
ticker = "NQ=F"
look_back = 20
vol_target = 1.5

try:
    # On prend plus de données (5d) pour bien calculer Tokyo
    df = yf.download(ticker, period="5d", interval="5m")
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # A. CALCUL DU RANGE DE TOKYO (00:00 - 08:00 UTC par défaut)
        df.index = pd.to_datetime(df.index)
        today = df.index[-1].date()
        tokyo_data = df.loc[str(today)].between_time('00:00', '08:00')
        
        if not tokyo_data.empty:
            tokyo_high = float(tokyo_data['High'].max())
            tokyo_low = float(tokyo_data['Low'].min())
        else:
            # Fallback si on est tôt le matin
            tokyo_high = 999999
            tokyo_low = 0

        # B. INDICATEURS CLASSIQUES
        df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
        v_ma = df['Volume'].rolling(20).mean()
        h_max_lb = df['High'].shift(1).rolling(look_back).max()
        l_min_lb = df['Low'].shift(1).rolling(look_back).min()

        # C. VALEURS ACTUELLES
        c_price = float(df['Close'].iloc[-1])
        c_high = float(df['High'].iloc[-1])
        c_low = float(df['Low'].iloc[-1])
        c_open = float(df['Open'].iloc[-1])
        c_vol = float(df['Volume'].iloc[-1])
        c_ema = float(df['ema200'].iloc[-1])

        # D. LOGIQUE REJET
        range_bar = c_high - c_low
        body_min = min(c_open, c_price)
        body_max = max(c_open, c_price)
        wick_down = body_min - c_low
        wick_up = c_high - body_max

        # ==========================================
        # 3. CONDITIONS SNIPER + SESSION
        # ==========================================
        # Filtre Tokyo
        is_above_tokyo = c_price > tokyo_high
        is_below_tokyo = c_price < tokyo_low

        # Alpha Sniper pur
        v_high = c_vol > (v_ma.iloc[-1] * vol_target)
        s_low = (c_low < l_min_lb.iloc[-1]) and (c_price > l_min_lb.iloc[-1])
        s_high = (c_high > h_max_lb.iloc[-1]) and (c_price < h_max_lb.iloc[-1])
        rej_bull = wick_down > (range_bar * 0.25)
        rej_bear = wick_up > (range_bar * 0.25)

        # SIGNAL FINAL AVEC CONFLUENCE TOKYO
        buy_signal = (c_price > c_ema) and s_low and v_high and rej_bull and is_above_tokyo
        sell_signal = (c_price < c_ema) and s_high and v_high and rej_bear and is_below_tokyo

        # ==========================================
        # 4. DASHBOARD & ALERTES
        # ==========================================
        col1, col2, col3 = st.columns(3)
        col1.metric("PRIX NQ", f"{c_price:.2f} $")
        col2.metric("TOKYO HIGH", f"{tokyo_high:.2f} $")
        col3.metric("TOKYO LOW", f"{tokyo_low:.2f} $")

        if buy_signal:
            st.success("🚀 BREAKOUT TOKYO + ALPHA BUY !")
            msg = f"🟢 *ALPHA TOKYO BREAKOUT BUY*\n\n*Prix:* {c_price:.2f}\n*Note:* Sortie de range Tokyo confirmée."
            if 'last_alert' not in st.session_state or st.session_state.last_alert != f"BUY_{c_price}":
                send_telegram(msg)
                st.session_state.last_alert = f"BUY_{c_price}"
                st.balloons()

        elif sell_signal:
            st.error("📉 BREAKOUT TOKYO + ALPHA SELL !")
            msg = f"🔴 *ALPHA TOKYO BREAKOUT SELL*\n\n*Prix:* {c_price:.2f}\n*Note:* Sortie de range Tokyo confirmée."
            if 'last_alert' not in st.session_state or st.session_state.last_alert != f"SELL_{c_price}":
                send_telegram(msg)
                st.session_state.last_alert = f"SELL_{c_price}"
                st.snow()
        else:
            st.info("Recherche de cassure de session propre...")

        # Visualisation
        st.line_chart(df[['Close', 'ema200']].tail(60))

except Exception as e:
    st.error(f"Erreur : {e}")

st.sidebar.markdown(f"### Paramètres\n- UT: 5m\n- Tokyo: 00h-08h\n- Multi Volume: {vol_target}")
