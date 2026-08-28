"""
app.py - Main Streamlit Entry Point for 11º Desafio JGP 2026 Quantitative Dashboard
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

# Inject custom Bloomberg Dark CSS styling
st.markdown("""
<style>
    /* Dark Theme Core Elements */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Header Container */
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
    
    /* Custom Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161A23;
        border-right: 1px solid #262B36;
    }
    
    /* Custom Metric Badges */
    .metric-badge-container {
        background-color: #1E222D;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid #262B36;
    }
    
    /* Streamlit Tabs Customization */
    button[data-baseweb="tab"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 12px 18px !important;
    }
    
    /* Hide default Streamlit footer */
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
# Sidebar Parameterization Controls
# -----------------------------------------------------------------------------
st.sidebar.markdown("### ⚙️ Parâmetros Regulamentares JGP")

# Preset Selector
date_preset = st.sidebar.selectbox(
    "Janela Temporal / Preset",
    options=[
        "Janela Tática JGP (16 Semanas / ~80 dias)",
        "Último 1 Ano (252 dias)",
        "Últimos 3 Anos",
        "Personalizado"
    ],
    index=0
)

# Date calculations
today = datetime.now()
if date_preset == "Janela Tática JGP (16 Semanas / ~80 dias)":
    start_dt = today - timedelta(days=120)  # ~80 trading days
    end_dt = today
elif date_preset == "Último 1 Ano (252 dias)":
    start_dt = today - timedelta(days=365)
    end_dt = today
elif date_preset == "Últimos 3 Anos":
    start_dt = today - timedelta(days=365 * 3)
    end_dt = today
else:
    col_d1, col_d2 = st.sidebar.columns(2)
    start_dt = col_d1.date_input("Início", today - timedelta(days=365))
    end_dt = col_d2.date_input("Fim", today)

start_str = start_dt.strftime("%Y-%m-%d")
end_str = end_dt.strftime("%Y-%m-%d")

# Regulatory Parameters Card in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="metric-badge-container">
    <h4 style="margin:0; color:#808A9D; font-size:12px;">HURDLE RATE (FED FUNDS)</h4>
    <h3 style="margin:4px 0; color:#FFD700; font-size:20px;">5.0% a.a.</h3>
    <p style="margin:0; color:#00E676; font-size:12px;"><b>+1.56%</b> pro rata (80 dias)</p>
    <hr style="border-color:#262B36; margin:8px 0;">
    <h4 style="margin:0; color:#808A9D; font-size:12px;">VOLATILIDADE PADRÃO JGP</h4>
    <p style="margin:2px 0 0 0; color:#FFFFFF; font-size:13px;"><b>20 dias úteis</b> (Factor √252)</p>
    <h4 style="margin:8px 0 0 0; color:#808A9D; font-size:12px;">CUSTO DE POSIÇÃO SHORT</h4>
    <p style="margin:2px 0 0 0; color:#FF5252; font-size:13px;"><b>0.4% a.m.</b> (~1/20 ao dia)</p>
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
    prices_df = data_loader.fetch_etf_data(
        tickers=config.ALL_ETFS,
        start_date=start_str,
        end_date=end_str
    )

# -----------------------------------------------------------------------------
# Main Application Tabs Navigation
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Performance & Hurdle",
    "🧩 Correlação & Ward",
    "🔍 Top 10 Holdings & HHI",
    "📐 Análise Técnica & Vol 20d",
    "🔄 Rotação Setorial & Markowitz",
    "🇧🇷 Eleições Brasil (EWZ)"
])

with tab1:
    tab1_performance.render_tab1(prices_df)

with tab2:
    tab2_correlation.render_tab2(prices_df)

with tab3:
    tab3_holdings.render_tab3()

with tab4:
    tab4_technical.render_tab4(prices_df)

with tab5:
    tab5_rotation.render_tab5(prices_df)

with tab6:
    tab6_elections.render_tab6()
