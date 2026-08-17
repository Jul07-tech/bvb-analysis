import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard BET Top 20 - Detalii Companii", layout="wide")

st.title("📈 Tablou de Bord Complet - Indicele BET (BVB)")
st.caption("Monitorizare interactivă și detalii despre companiile din indicele principal")

TICKERS = [
    "TLV.RO", "SNP.RO", "H2O.RO", "SNG.RO", "BRD.RO", 
    "DIGI.RO", "SNN.RO", "TGN.RO", "EL.RO", "M.RO",
    "FP.RO", "WNS.RO", "ONE.RO", "AQ.RO", "TTS.RO",
    "TEL.RO", "BVB.RO", "SFG.RO", "PE.RO", "ATB.RO"
]

st.sidebar.header("⚙️ Setări & Filtre")
period = st.sidebar.selectbox(
    "Selectează perioada de analiză:",
    options=["1d", "5d", "1mo", "6mo", "1y", "ytd"],
    format_func=lambda x: {
        "1d": "Azi", "5d": "Ultimile 5 zile", "1mo": "Ultima lună", 
        "6mo": "Ultimele 6 luni", "1y": "Ultimul an", "ytd": "De la începutul anului"
    }[x],
    index=2
)

@st.cache_data(ttl=3600)
def load_bet_data(tickers, period):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            info = stock.info
            
            if not df.empty:
                start_price = df['Close'].iloc[0]
                end_price = df['Close'].iloc[-1]
                pct_change = ((end_price - start_price) / start_price) * 100
                
                market_cap = info.get('marketCap', 0)
                market_cap_mld = round(market_cap / 1e9, 2) if market_cap else 0
                
                data.append({
                    "Simbol": ticker.replace(".RO", ""),
                    "Nume Companie": info.get('longName', ticker.replace(".RO", "")),
                    "Sector": info.get('sector', 'N/A'),
                    "Industrie": info.get('industry', 'N/A'),
                    "Preț Curent (RON)": round(end_price, 2),
                    "Variație (%)": round(pct_change, 2),
                    "Capitalizare (Mld RON)": market_cap_mld,
                    "Volum Mediu": int(df['Volume'].mean()),
                    "Descriere": info.get('longBusinessSummary', 'Fără descriere disponibilă.'),
                    "Website": info.get('website', '#'),
                    "PER (P/E Ratio)": info.get('trailingPE', 'N/A'),
                    "Max 52 Wk (RON)": info.get('fiftyTwoWeekHigh', 'N/A'),
                    "Min 52 Wk (RON)": info.get('fiftyTwoWeekLow', 'N/A')
                })
        except Exception:
            continue
    return data

data = load_bet_data(TICKERS, period)

if data:
    df_results = pd.DataFrame(data)
    df_results = df_results.sort_values(by="Variație (%)", ascending=False).reset_index(drop=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Top Randament", f"{df_results.iloc[0]['Simbol']}", f"{df_results.iloc[0]['Variație (%)']}%")
    col2.metric("Lider Capitalizare", f"{df_results.sort_values(by='Capitalizare (Mld RON)', ascending=False).iloc[0]['Simbol']}", f"{df_results['Capitalizare (Mld RON)'].max()} mld RON")
    col3.metric("Medie Variație BET", f"{round(df_results['Variație (%)'].mean(), 2)}%")
    col4.metric("Total Companii Monitorizate", len(df_results))

    st.markdown("---")

    st.subheader("📊 Randamente Companii (Pune mouse-ul pe bare pentru detalii)")
    fig_perf = px.bar(
        df_results, 
        x="Simbol", 
        y="Variație (%)", 
        color="Variație (%)",
        hover_data=["Nume Companie", "Sector", "Preț Curent (RON)", "Capitalizare (Mld RON)"],
        title=f"Evoluția Prețului pentru Companiile BET ({period})",
        color_continuous_scale=["#FF4B4B", "#CCCCCC", "#00CC66"],
        text_auto=True
    )
    st.plotly_chart(fig_perf, use_container_width=True)

    st.markdown("---")

    st.subheader("🔍 Fișă Tehnică & Detalii Companie")
    selected_symbol = st.selectbox("Alege compania pentru a-i vedea profilul complet:", df_results["Simbol"].tolist())

    company_info = df_results[df_results["Simbol"] == selected_symbol].iloc[0]

    c1, c2 = st.columns([1, 2])

    with c1:
        st.markdown(f"### **{company_info['Nume Companie']}** ({company_info['Simbol']})")
        st.write(f"**Sector:** {company_info['Sector']}")
        st.write(f"**Industrie:** {company_info['Industrie']}")
        st.write(f"**Preț Curent:** {company_info['Preț Curent (RON)']} RON")
        st.write(f"**P/E Ratio (PER):** {company_info['PER (P/E Ratio)']}")
        st.write(f"**Max / Min 52 săptămâni:** {company_info['Max 52 Wk (RON)']} / {company_info['Min 52 Wk (RON)']} RON")
        if company_info['Website'] != '#':
            st.markdown(f"🌐 [Vizitează Site-ul Oficial]({company_info['Website']})")

    with c2:
        st.markdown("#### **Descriere Activitate**")
        st.info(company_info['Descriere'])

    st.markdown("---")

    st.subheader("📋 Tabel Sumar BET")
    st.dataframe(
        df_results[["Simbol", "Nume Companie", "Preț Curent (RON)", "Variație (%)", "Capitalizare (Mld RON)", "Sector"]],
        use_container_width=True
    )
else:
    st.error("Nu s-au putut prelua datele de pe Yahoo Finance. Încearcă din nou în câteva minute.")
