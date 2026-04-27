import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. CONFIGURATION (TES INFOS)
# ==========================================
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQOAWZCJ-vMQ"
CHAT_ID = "7836102896"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except Exception as e:
        st.error(f"Erreur Telegram : {e}")

# ==========================================
# 2. INTERFACE & REFRESH
# ==========================================
st.set_page_config(page_title="ALPHA SNIPER NQ", page_icon="🛡️", layout="wide")

# Refresh automatique toutes les 60 secondes
st_autorefresh(interval=60000, key="alpha_refresh")

st.title("🛡️ ALPHA SNIPER NQ - LIVE")
st.caption(f"Système de scan automatique actif • {datetime.now().strftime('%H:%M:%S')}")

# --- TEST DE CONNEXION INITIAL ---
if 'test_sent' not in st.session_state:
    send_telegram("🚀 *Système Alpha Sniper opérationnel !* \nRecherche de signaux sur le Nasdaq (NQ=F) activée.")
    st.session_state.test_sent = True

# ==========================================
# 3. ANALYSE TECHNIQUE (LOGIQUE PINE SCRIPT)
# ==========================================
ticker = "NQ=F"
vol_target = 1.5
look_back = 20

try:
    # On télécharge les données (intervalle 5m ou 15m selon ta préférence sur TradingView)
    df = yf.download(ticker, period="2d", interval="5m")
    
    if not df.empty:
        # Nettoyage des colonnes yfinance (pour éviter l'erreur Series/MultiIndex)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # A. EMA 200
        df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # B. VOLUME MOYEN (SMA 20)
        v_ma = df['Volume'].rolling(20).mean()
        
        # C. LIQUIDITÉ (Plus haut/bas des 20 dernières bougies)
        h_max = df['High'].shift(1).rolling(look_back).max()
        l_min = df['Low'].shift(1).rolling(look_back).min()

        # D. VALEURS ACTUELLES (Bougie en cours)
        c_price = float(df['Close'].iloc[-1])
        c_high = float(df['High'].iloc[-1])
        c_low = float(df['Low'].iloc[-1])
        c_open = float(df['Open'].iloc[-1])
        c_vol = float(df['Volume'].iloc[-1])
        c_ema = float(df['ema200'].iloc[-1])
        
        # E. LOGIQUE DES MÈCHES (REJET)
        range_bar = c_high - c_low
        body_min = min(c_open, c_price)
        body_max = max(c_open, c_price)
        wick_down = body_min - c_low
        wick_up = c_high - body_max

        # --- CONDITIONS ALPHA SNIPER ---
        is_bull = c_price > c_ema
        is_bear = c_price < c_ema
        v_high = c_vol > (v_ma.iloc[-1] * vol_target)
        
        # Sweep & Rejet
        s_low = (c_low < l_min.iloc[-1]) and (c_price > l_min.iloc[-1])
        s_high = (c_high > h_max.iloc[-1]) and (c_price < h_max.iloc[-1])
        rej_bull = wick_down > (range_bar * 0.25)
        rej_bear = wick_up > (range_bar * 0.25)

        # --- DÉTECTION SIGNAUX ---
        buy_signal = is_bull and s_low and v_high and rej_bull
        sell_signal = is_bear and s_high and v_high and rej_bear

        # ==========================================
        # 4. AFFICHAGE & ALERTES
        # ==========================================
        col1, col2 = st.columns(2)
        col1.metric("PRIX NASDAQ (NQ=F)", f"{c_price:.2f} $")
        
        if buy_signal:
            st.success("🔥 SIGNAL D'ACHAT ALPHA DÉTECTÉ !")
            msg = f"🟢 *ALPHA BUY SIGNAL*\n\n*Prix:* {c_price:.2f}\n*Tendance:* Haussière\n*Volume:* Explosion confirmée\n*Liquidité:* Sweep validé"
            # Anti-spam : n'envoie que si le prix a changé
            if 'last_alert' not in st.session_state or st.session_state.last_alert != f"BUY_{c_price}":
                send_telegram(msg)
                st.session_state.last_alert = f"BUY_{c_price}"
                st.balloons()
                
        elif sell_signal:
            st.error("📉 SIGNAL DE VENTE ALPHA DÉTECTÉ !")
            msg = f"🔴 *ALPHA SELL SIGNAL*\n\n*Prix:* {c_price:.2f}\n*Tendance:* Baissière\n*Volume:* Explosion confirmée\n*Liquidité:* Sweep validé"
            if 'last_alert' not in st.session_state or st.session_state.last_alert != f"SELL_{c_price}":
                send_telegram(msg)
                st.session_state.last_alert = f"SELL_{c_price}"
                st.snow()
        else:
            col2.info("Analyse du marché en cours : Aucun signal Sniper pour le moment.")

        # Graphique de contrôle
        st.line_chart(df[['Close', 'ema200']].tail(50))

    else:
        st.warning("En attente de réception des données Yahoo Finance...")

except Exception as e:
    st.error(f"Erreur technique : {e}")

st.sidebar.markdown(f"### Statut du Bot\n✅ Opérationnel\n⏰ Intervalle : 60s\n🎯 Ticker : {ticker}")
