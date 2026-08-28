"""
app.py - Expanded Main Streamlit Entry Point for 11º Desafio JGP 2026 Quantitative Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import config
import data_loader
import metrics
from modules import (
    tab1_performance,
    tab2_correlation,
    tab3_holdings,
    tab4_technical,
    tab5_rotation,
    tab6_elections
)

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Dark Bloomberg/Quant CSS Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Quantitativo - 11º Desafio JGP 2026",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    .jgp-header {
        background: linear-gradient(90deg, #1A1F2C 0%, #0E1117 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2962FF;
        margin-bottom: 25px;
    }
    .jgp-header h1 {
        color: #FFFFFF;
        font-weight: 700;
        margin: 0;
        font-size: 26px;
        letter-spacing: -0.5px;
    }
    .jgp-header p {
        color: #808A9D;
        margin: 5px 0 0 0;
        font-size: 14px;
    }
    section[data-testid="stSidebar"] {
        background-color: #161A23;
        border-right: 1px solid #262B36;
    }
    .metric-badge-container {
        background-color: #1E222D;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid #262B36;
    }
    button[data-baseweb="tab"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 12px 18px !important;
    }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Header Banner
# -----------------------------------------------------------------------------
st.markdown("""
<div class="jgp-header">
    <h1>📈 DASHBOARD QUANTITATIVO - 11º DESAFIO JGP (2026)</h1>
    <p>Alocação em ETFs Globais, Gestão de Risco, Decomposição de Holdings & Análise de Ciclos Eleitorais B3</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar Controls & Expanded Feature 1: Macro Base Window (1 to 3 Years)
# -----------------------------------------------------------------------------
st.sidebar.markdown("### ⚙️ Parâmetros Regulamentares & Macro")

macro_period_label = st.sidebar.selectbox(
    "Janela Base Macro (Amostra Estatística)",
    options=list(config.MACRO_WINDOWS.keys()),
    index=1,  # Default 2 Anos (504d)
    help="Define o número de dias úteis (252 a 756d) para a matriz de covariância, correlação e Fronteira de Markowitz."
)

days_lookback = config.MACRO_WINDOWS[macro_period_label]

date_preset = st.sidebar.selectbox(
    "Filtro Visual Principal",
    options=[
        "Janela Base Macro Selecionada",
        "Janela Tática JGP (16 Semanas / ~80 dias)",
        "Personalizado"
    ],
    index=0
)

today = datetime.now()
if date_preset == "Janela Base Macro Selecionada":
    start_dt = today - timedelta(days=int(days_lookback * 1.45))
    end_dt = today
elif date_preset == "Janela Tática JGP (16 Semanas / ~80 dias)":
    start_dt = today - timedelta(days=120)
    end_dt = today
else:
    col_d1, col_d2 = st.sidebar.columns(2)
    start_dt = col_d1.date_input("Início", today - timedelta(days=365))
    end_dt = col_d2.date_input("Fim", today)

start_str = start_dt.strftime("%Y-%m-%d")
end_str = end_dt.strftime("%Y-%m-%d")

# Sidebar Metrics Card
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div class="metric-badge-container">
    <h4 style="margin:0; color:#808A9D; font-size:12px;">AMOSTRA ESTATÍSTICA MACRO</h4>
    <h3 style="margin:4px 0; color:#00E5FF; font-size:18px;">{days_lookback} Pregões Úteis</h3>
    <hr style="border-color:#262B36; margin:8px 0;">
    <h4 style="margin:0; color:#808A9D; font-size:12px;">HURDLE RATE (FED FUNDS)</h4>
    <h3 style="margin:4px 0; color:#FFD700; font-size:18px;">5.0% a.a. (+1.56% tático)</h3>
    <h4 style="margin:8px 0 0 0; color:#808A9D; font-size:12px;">VOLATILIDADE PADRÃO JGP</h4>
    <p style="margin:2px 0 0 0; color:#FFFFFF; font-size:13px;"><b>20 dias úteis</b> (Factor √252)</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Atualizar Cache de Dados"):
    st.cache_data.clear()
    st.sidebar.success("Cache atualizado!")

# -----------------------------------------------------------------------------
# Data Loading Pipeline
# -----------------------------------------------------------------------------
with st.spinner("Buscando e processando cotações via Yahoo Finance..."):
    # Load dataset starting from 2015 to support 1-3 yr macro window and 5-10 yr seasonality
    prices_df = data_loader.fetch_etf_data(
        tickers=config.ALL_ETFS,
        start_date="2015-01-01",
        end_date=end_str
    )

# Slice prices DataFrame according to selected start/end dates for visual display
if not prices_df.empty:
    sub_prices_df = prices_df.loc[(prices_df.index >= start_str) & (prices_df.index <= end_str)]
    if sub_prices_df.empty or len(sub_prices_df) < 20:
        sub_prices_df = prices_df.tail(days_lookback)
else:
    sub_prices_df = pd.DataFrame()

# -----------------------------------------------------------------------------
# Main Application Tabs Navigation
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Performance & Sazonalidade (Ago-Dez)",
    "🧩 Correlação & Ward (Lookback)",
    "🔍 Top 10 Holdings & HHI",
    "📐 Análise Técnica & Vol 20d (1M/3M)",
    "🔄 Rotação Setorial & Markowitz Macro",
    "🇧🇷 Eleições Brasil (EWZ)"
])

with tab1:
    tab1_performance.render_tab1(sub_prices_df, full_prices_df=prices_df)

with tab2:
    tab2_correlation.render_tab2(sub_prices_df)

with tab3:
    tab3_holdings.render_tab3()

with tab4:
    tab4_technical.render_tab4(sub_prices_df, full_prices_df=prices_df)

with tab5:
    tab5_rotation.render_tab5(sub_prices_df)

with tab6:
    tab6_elections.render_tab6()
