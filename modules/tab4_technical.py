"""
tab4_technical.py - Tab 4: Individual Technical Analysis, Volatility Regime (20d JGP Standard) & Z-Score
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import config
import metrics
import data_loader


def render_tab4(prices_df: pd.DataFrame):
    st.markdown("## 📐 Módulo 4: Análise Técnica Individual, Regime e Volatilidade (20d JGP)")
    st.caption("Painel individual para calibração de pontos de entrada/saída tática, monitoramento da volatilidade móvel oficial de 20 dias e oscilador de reversão à média (Z-Score).")

    if prices_df.empty:
        st.error("Dados não disponíveis para o Módulo 4.")
        return

    # Select target asset
    col_t1, col_t2 = st.columns([2, 2])
    with col_t1:
        target_asset = st.selectbox(
            "Selecionar Ativo para Análise Técnica",
            options=list(prices_df.columns),
            index=list(prices_df.columns).index("SPY") if "SPY" in prices_df.columns else 0,
            key="tab4_asset_select"
        )
    with col_t2:
        chart_style = st.radio(
            "Estilo de Gráfico Principal",
            options=["Candlestick OHLC", "Preço de Fechamento Line"],
            index=0,
            horizontal=True,
            key="tab4_chart_style"
        )

    # Fetch full OHLCV or use price series
    ohlc_df = data_loader.fetch_single_ticker_ohlcv(target_asset, start_date="2022-01-01")
    
    if ohlc_df.empty or "Close" not in ohlc_df.columns:
        series_price = prices_df[target_asset]
    else:
        series_price = ohlc_df["Close"]

    tech_df = metrics.calculate_technical_indicators(series_price)
    
    if "Open" in ohlc_df.columns:
        tech_df["Open"] = ohlc_df["Open"]
        tech_df["High"] = ohlc_df["High"]
        tech_df["Low"] = ohlc_df["Low"]
        tech_df["Close"] = ohlc_df["Close"]

    tech_df = tech_df.dropna(subset=["Price"])

    # -------------------------------------------------------------------------
    # 3-Panel Subplots Figure
    # -------------------------------------------------------------------------
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=(
            f"<b>Panel 1: Preço & Tendência - {target_asset} ({config.ETF_NAMES.get(target_asset, '')})</b>",
            "<b>Panel 2: Regime de Volatilidade Anualizada (20d JGP vs 60d Trend)</b>",
            "<b>Panel 3: Oscilador Z-Score (Desvio da SMA200)</b>"
        ),
        row_heights=[0.50, 0.25, 0.25]
    )

    # Panel 1: Price & Technical Overlays
    if chart_style == "Candlestick OHLC" and "Open" in tech_df.columns:
        fig.add_trace(go.Candlestick(
            x=tech_df.index,
            open=tech_df["Open"],
            high=tech_df["High"],
            low=tech_df["Low"],
            close=tech_df["Close"],
            name="OHLC",
            increasing_line_color="#00E676",
            decreasing_line_color="#FF5252"
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=tech_df.index,
            y=tech_df["Price"],
            mode="lines",
            name="Preço",
            line=dict(color="#2962FF", width=2.0)
        ), row=1, col=1)

    # Add SMA50, SMA200, Bollinger Bands
    fig.add_trace(go.Scatter(
        x=tech_df.index, y=tech_df["SMA50"],
        mode="lines", name="SMA 50", line=dict(color="#FFEA00", width=1.5)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=tech_df.index, y=tech_df["SMA200"],
        mode="lines", name="SMA 200", line=dict(color="#E040FB", width=1.8)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=tech_df.index, y=tech_df["Bollinger_Upper"],
        mode="lines", name="Bollinger Sup", line=dict(color="#90A4AE", width=1.0, dash="dash")
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=tech_df.index, y=tech_df["Bollinger_Lower"],
        mode="lines", name="Bollinger Inf", line=dict(color="#90A4AE", width=1.0, dash="dash"),
        fill="tonexty", fillcolor="rgba(144, 164, 174, 0.08)"
    ), row=1, col=1)

    # Panel 2: Volatility Regime 20d (JGP) vs 60d
    fig.add_trace(go.Scatter(
        x=tech_df.index, y=tech_df["Vol_20d_JGP"],
        mode="lines", name="Vol 20d (Oficial JGP)", line=dict(color="#FF6D00", width=2.2)
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=tech_df.index, y=tech_df["Vol_60d_Trend"],
        mode="lines", name="Vol 60d (Tendência)", line=dict(color="#78909C", width=1.5, dash="dot")
    ), row=2, col=1)

    # Panel 3: Z-Score Oscillator
    fig.add_trace(go.Scatter(
        x=tech_df.index, y=tech_df["Z_Score_200"],
        mode="lines", name="Z-Score (SMA200)", line=dict(color="#00E5FF", width=1.8)
    ), row=3, col=1)

    # Add Z-Score reference thresholds (+2.0, 0.0, -2.0)
    fig.add_shape(type="line", x0=tech_df.index[0], x1=tech_df.index[-1], y0=2.0, y1=2.0,
                  line=dict(color="#FF5252", width=1.2, dash="dash"), row=3, col=1)
    fig.add_shape(type="line", x0=tech_df.index[0], x1=tech_df.index[-1], y0=0.0, y1=0.0,
                  line=dict(color="#FFFFFF", width=0.8, dash="dot"), row=3, col=1)
    fig.add_shape(type="line", x0=tech_df.index[0], x1=tech_df.index[-1], y0=-2.0, y1=-2.0,
                  line=dict(color="#00E676", width=1.2, dash="dash"), row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=800,
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis3=dict(showgrid=True, gridcolor="#333333"),
        yaxis1=dict(title="Preço (USD)", showgrid=True, gridcolor="#333333"),
        yaxis2=dict(title="Vol. Anualizada (%)", showgrid=True, gridcolor="#333333"),
        yaxis3=dict(title="Z-Score (σ)", showgrid=True, gridcolor="#333333", range=[-3.5, 3.5])
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------------------------
    # Latest Indicators Summary Metric Cards
    # -------------------------------------------------------------------------
    st.markdown("### 📋 Resumo das Métricas Técnicas Recentes")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    latest = tech_df.iloc[-1]
    curr_price = latest["Price"]
    curr_vol20 = latest["Vol_20d_JGP"]
    curr_vol60 = latest["Vol_60d_Trend"]
    curr_z = latest["Z_Score_200"]

    m_col1.metric("Preço Atual", f"${curr_price:.2f}")
    m_col2.metric("Volatilidade 20d (JGP)", f"{curr_vol20:.1f}%", f"{curr_vol20 - curr_vol60:+.1f}% vs 60d")
    m_col3.metric("Z-Score (SMA200)", f"{curr_z:+.2f}σ", "Sobrecomprado" if curr_z > 2.0 else "Sobrevendido" if curr_z < -2.0 else "Neutro")
    
    sma200_dist = ((curr_price / latest["SMA200"]) - 1.0) * 100.0 if pd.notnull(latest["SMA200"]) else 0.0
    m_col4.metric("Distância da SMA200", f"{sma200_dist:+.2f}%")
