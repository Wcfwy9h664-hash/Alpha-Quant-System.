if st.sidebar.button("Lancer le Scan Manuel"):
    # Récupération des données
    data = yf.download(ticker, period="1d", interval=interval)
    
    if not data.empty:
        # --- LIGNE DE CORRECTION ---
        # On s'assure que les colonnes sont simples (High, Low, Close)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        
        current_price = float(data['Close'].iloc[-1])
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
