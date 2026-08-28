"""
tab2_correlation.py - Tab 2: 18x18 Interactive Correlation Matrix, Ward Clustering & Rolling Correlation
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import config
import metrics


def render_tab2(prices_df: pd.DataFrame):
    st.markdown("## 🧩 Módulo 2: Matriz de Correlação & Heatmap Clustered (Ward)")
    st.caption("Mapeamento da estrutura de dependência estatística e risco de contágio entre os 18 ETFs elegíveis para identificação de hedges e pares descorrelacionados.")

    if prices_df.empty:
        st.error("Dados de preços não disponíveis para o Módulo 2.")
        return

    # Lookback controls
    col_c1, col_c2 = st.columns([2, 2])
    with col_c1:
        lookback_days = st.selectbox(
            "Janela Temporal de Análise (Lookback)",
            options=[20, 60, 120, 252],
            index=0,  # Default 20d (JGP standard)
            format_func=lambda x: f"{x} dias úteis" + (" (Janela Oficial JGP)" if x == 20 else ""),
            key="tab2_lookback"
        )
    with col_c2:
        apply_clustering = st.checkbox(
            "Aplicar Clusterização Hierárquica (Ward's Linkage)",
            value=True,
            key="tab2_clustering_check"
        )

    # Filter tickers present in prices DataFrame
    avail_etfs = [t for t in config.ALL_ETFS if t in prices_df.columns]
    if len(avail_etfs) < 2:
        st.warning("Insuficiência de ativos disponíveis para gerar a matriz de correlação.")
        return

    sub_prices = prices_df[avail_etfs]
    
    # Calculate Correlation Matrix
    corr_matrix = metrics.calculate_correlation_matrix(sub_prices, window=lookback_days)

    if apply_clustering:
        reordered_corr, linkage_matrix = metrics.perform_ward_clustering(corr_matrix)
        display_corr = reordered_corr
    else:
        display_corr = corr_matrix

    # -------------------------------------------------------------------------
    # Chart 2A: 18x18 Interactive Correlation Heatmap
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown(f"### 🌡️ Gráfico 2A - Heatmap de Correlação ({lookback_days} Pregões)" + (" [Clustered - Enlace de Ward]" if apply_clustering else ""))

    # Prepare annotations text matrix formatted to 2 decimal places
    z_vals = display_corr.values
    x_labels = list(display_corr.columns)
    y_labels = list(display_corr.index)
    
    text_vals = np.around(z_vals, 2).astype(str)

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=z_vals,
        x=x_labels,
        y=y_labels,
        text=text_vals,
        texttemplate="%{text}",
        textfont=dict(size=10, color="white"),
        colorscale=[
            [0.0, "#2196F3"],   # Blue for -1.0
            [0.5, "#121212"],   # Neutral dark background for 0.0
            [1.0, "#FF5252"]    # Red for +1.0
        ],
        zmin=-1.0,
        zmax=1.0,
        colorbar=dict(title="Correlação (ρ)", tickvals=[-1.0, -0.5, 0.0, 0.5, 1.0])
    ))

    fig_heatmap.update_layout(
        template="plotly_dark",
        height=620,
        margin=dict(l=50, r=50, t=40, b=50),
        xaxis=dict(tickangle=-45, showgrid=False),
        yaxis=dict(showgrid=False, autorange="reversed")
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    # -------------------------------------------------------------------------
    # Chart 2B: Rolling Correlation (20d & 60d) vs SPY / TLT
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📉 Gráfico 2B - Correlação Móvel (Rolling Correlation 20d & 60d)")
    st.caption("Acompanhamento da estabilidade das relações de contágio ou diversificação ao longo do tempo.")

    col_r1, col_r2 = st.columns([2, 2])
    with col_r1:
        target_asset = st.selectbox(
            "Ativo sob Análise",
            options=[t for t in avail_etfs if t not in ["SPY", "TLT"]],
            index=0,
            key="tab2_target_asset"
        )
    with col_r2:
        benchmark_target = st.selectbox(
            "Ativo de Referência / Hedge",
            options=["SPY", "TLT"],
            index=0,
            key="tab2_benchmark_target"
        )

    df_rolling = metrics.calculate_rolling_correlation(
        prices_df,
        asset1=target_asset,
        asset2=benchmark_target,
        windows=[20, 60]
    )

    if not df_rolling.empty:
        fig_roll = go.Figure()

        if "Corr 20d" in df_rolling.columns:
            fig_roll.add_trace(go.Scatter(
                x=df_rolling.index,
                y=df_rolling["Corr 20d"],
                mode="lines",
                name="Correlação 20d (Janela JGP)",
                line=dict(color="#FF9800", width=2.2)
            ))
            
        if "Corr 60d" in df_rolling.columns:
            fig_roll.add_trace(go.Scatter(
                x=df_rolling.index,
                y=df_rolling["Corr 60d"],
                mode="lines",
                name="Correlação 60d (Tendência)",
                line=dict(color="#90A4AE", width=1.8, dash="dot")
            ))

        # Add zero-correlation reference line
        fig_roll.add_shape(
            type="line",
            x0=df_rolling.index[0],
            x1=df_rolling.index[-1],
            y0=0.0,
            y1=0.0,
            line=dict(color="#FFFFFF", width=1.0, dash="dash")
        )

        fig_roll.update_layout(
            template="plotly_dark",
            height=420,
            margin=dict(l=40, r=40, t=40, b=40),
            title=dict(text=f"Correlação Rolante: <b>{target_asset}</b> vs. <b>{benchmark_target}</b>"),
            xaxis=dict(showgrid=True, gridcolor="#333333"),
            yaxis=dict(title="Coeficiente ρ", range=[-1.05, 1.05], showgrid=True, gridcolor="#333333"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_roll, use_container_width=True)
