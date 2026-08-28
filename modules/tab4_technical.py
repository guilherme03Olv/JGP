"""
tab4_technical.py - Tab 4: Technical Analysis, 20d Rolling Volatility Regime & Short-Term Tactical Metrics
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional
import config
import metrics
import data_loader


def render_tab4(prices_df: pd.DataFrame, full_prices_df: Optional[pd.DataFrame] = None):
    st.markdown("## 📐 Módulo 4: Análise Técnica, Regime e Métricas Móveis de Curto Prazo")
    st.caption("Painel individual para sensibilidade tática, monitoramento da volatilidade móvel oficial de 20 dias, retornos de 1M/3M e oscilador Z-Score.")

    if prices_df.empty:
        st.error("Dados não disponíveis para o Módulo 4.")
        return

    if full_prices_df is None or full_prices_df.empty:
        full_prices_df = prices_df

    # Select target asset
    col_t1, col_t2 = st.columns([2, 2])
    with col_t1:
        target_asset = st.selectbox(
            "Selecionar Ativo para Análise Técnica e Sensibilidade",
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
    ohlc_df = data_loader.fetch_single_ticker_ohlcv(target_asset, start_date="2021-01-01")
    
    if ohlc_df.empty or "Close" not in ohlc_df.columns:
        full_series = full_prices_df[target_asset] if target_asset in full_prices_df.columns else prices_df[target_asset]
    else:
        full_series = ohlc_df["Close"]

    # Calculate technical indicators on FULL history so SMA200 and Z-Score are populated
    full_tech_df = metrics.calculate_technical_indicators(full_series)
    
    if "Open" in ohlc_df.columns:
        full_tech_df["Open"] = ohlc_df["Open"]
        full_tech_df["High"] = ohlc_df["High"]
        full_tech_df["Low"] = ohlc_df["Low"]
        full_tech_df["Close"] = ohlc_df["Close"]

    # Filter tech_df to display timeframe
    display_start = prices_df.index[0]
    tech_df = full_tech_df.loc[full_tech_df.index >= display_start].dropna(subset=["Price"])
    if tech_df.empty:
        tech_df = full_tech_df.tail(252).dropna(subset=["Price"])

    # -------------------------------------------------------------------------
    # Expanded Feature 3: Short-Term Tactical Metrics Cards (20d Vol, 1M/21d & 3M/63d)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### ⚡ Métricas Móveis de Curto Prazo & Regime de Volatilidade (Timing)")

    short_metrics = metrics.calculate_short_term_metrics(full_series)

    if short_metrics:
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        
        curr_vol = short_metrics["Current_Vol_20d"]
        hist_mean_vol = short_metrics["Hist_Mean_Vol"]
        vol_delta = short_metrics["Vol_Delta_Vs_Mean"]
        ret_1m = short_metrics["Ret_1M_21d"]
        ret_3m = short_metrics["Ret_3M_63d"]
        regime = short_metrics["Regime"]
        regime_badge = short_metrics["Regime_Badge"]

        badge_col = "#00E676" if regime_badge == "success" else "#FFB300" if regime_badge == "warning" else "#FF5252"

        c_m1.metric(
            label="Volatilidade Móvel 20d (Anualizada)",
            value=f"{curr_vol:.1f}%",
            delta=f"{vol_delta:+.1f}% vs Média Histórica ({hist_mean_vol:.1f}%)",
            delta_color="inverse"
        )
        
        c_m2.metric(
            label="Retorno 1 Mês (21 Pregões)",
            value=f"{ret_1m:+.2f}%",
            delta=f"{ret_1m - ret_3m:+.2f}% vs 3M"
        )
        
        c_m3.metric(
            label="Retorno 3 Meses (63 Pregões)",
            value=f"{ret_3m:+.2f}%"
        )

        c_m4.markdown(f"""
        <div style="background-color: #1E222D; padding: 12px; border-radius: 8px; border-top: 4px solid {badge_col}; text-align: center;">
            <h5 style="margin:0; color:#808A9D; font-size:11px;">REGIME DE VOLATILIDADE ATUAL</h5>
            <p style="margin:6px 0 0 0; color:{badge_col}; font-size:13px; font-weight:bold;">{regime}</p>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3-Panel Subplots Figure (Price, 20d Rolling Volatility, Z-Score)
    # -------------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=(
            f"<b>Panel 1: Preço & Tendência - {target_asset} ({config.ETF_NAMES.get(target_asset, '')})</b>",
            "<b>Panel 2: Volatilidade Móvel 20d Anualizada (%) vs Média Histórica</b>",
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

    # Panel 2: Interactive 20d Rolling Volatility over time vs Historical Mean
    fig.add_trace(go.Scatter(
        x=tech_df.index, y=tech_df["Vol_20d_JGP"],
        mode="lines", name="Vol 20d (Oficial JGP)", line=dict(color="#FF6D00", width=2.2)
    ), row=2, col=1)

    if short_metrics:
        fig.add_shape(
            type="line",
            x0=tech_df.index[0], x1=tech_df.index[-1],
            y0=short_metrics["Hist_Mean_Vol"], y1=short_metrics["Hist_Mean_Vol"],
            line=dict(color="#FFD700", width=1.5, dash="dash"),
            row=2, col=1
        )

    # Panel 3: Z-Score Oscillator
    fig.add_trace(go.Scatter(
        x=tech_df.index, y=tech_df["Z_Score_200"],
        mode="lines", name="Z-Score (SMA200)", line=dict(color="#00E5FF", width=1.8)
    ), row=3, col=1)

    fig.add_shape(type="line", x0=tech_df.index[0], x1=tech_df.index[-1], y0=2.0, y1=2.0,
                  line=dict(color="#FF5252", width=1.2, dash="dash"), row=3, col=1)
    fig.add_shape(type="line", x0=tech_df.index[0], x1=tech_df.index[-1], y0=0.0, y1=0.0,
                  line=dict(color="#FFFFFF", width=0.8, dash="dot"), row=3, col=1)
    fig.add_shape(type="line", x0=tech_df.index[0], x1=tech_df.index[-1], y0=-2.0, y1=-2.0,
                  line=dict(color="#00E676", width=1.2, dash="dash"), row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=820,
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis3=dict(showgrid=True, gridcolor="#333333"),
        yaxis1=dict(title="Preço (USD)", showgrid=True, gridcolor="#333333"),
        yaxis2=dict(title="Vol. Anualizada (%)", showgrid=True, gridcolor="#333333"),
        yaxis3=dict(title="Z-Score (σ)", showgrid=True, gridcolor="#333333", range=[-3.5, 3.5])
    )

    st.plotly_chart(fig, use_container_width=True)
