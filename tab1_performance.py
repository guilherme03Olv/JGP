"""
tab1_performance.py - Tab 1: Tactical Performance vs Hurdle Rate & Expanded Seasonality (Aug-Dec, 5-10 Years)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional
import config
import metrics


def render_tab1(prices_df: pd.DataFrame, full_prices_df: Optional[pd.DataFrame] = None):
    st.markdown("## 📈 Módulo 1: Performance Tática vs. Hurdle Rate & Sazonalidade Homóloga (Ago - Dez)")
    st.caption("Identificação de alfa real sobre o caixa JGP (+1,56% nas 16 semanas / 5,0% a.a.) e análise de sazonalidade do rali de fim de ano (Agosto a Dezembro) nos últimos 5 a 10 anos.")

    if prices_df.empty:
        st.error("Dados de preços não disponíveis para processamento do Módulo 1.")
        return

    if full_prices_df is None or full_prices_df.empty:
        full_prices_df = prices_df

    # Top Controls & Filters
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])
    
    with col_ctrl1:
        category_filter = st.multiselect(
            "Filtrar Categoria de ETFs",
            options=list(config.ETF_CATEGORIES.keys()),
            default=list(config.ETF_CATEGORIES.keys()),
            key="tab1_category_filter"
        )
        
    with col_ctrl2:
        strategy_mode = st.radio(
            "Modo de Posição",
            options=["Long (Comprado)", "Short (Vendido com Custo 0.4% a.m.)"],
            index=0,
            horizontal=True,
            key="tab1_strategy_mode"
        )
        
    with col_ctrl3:
        normalizer_base = st.selectbox(
            "Formato de Retorno Visual",
            options=["Retorno Percentual (%)", "Base 100"],
            index=0,
            key="tab1_normalizer"
        )

    # Filter selected tickers
    selected_tickers = []
    for cat in category_filter:
        selected_tickers.extend(config.ETF_CATEGORIES[cat])
    selected_tickers = list(dict.fromkeys(selected_tickers))
    
    avail_tickers = [t for t in selected_tickers if t in prices_df.columns]
    if not avail_tickers:
        st.warning("Nenhum ativo selecionado disponível nos dados.")
        return
        
    sub_prices = prices_df[avail_tickers]

    # Calculate returns (Long vs Short)
    if "Short" in strategy_mode:
        cum_returns = metrics.calculate_short_returns(sub_prices)
    else:
        cum_returns = metrics.calculate_cumulative_returns(sub_prices)

    # -------------------------------------------------------------------------
    # Chart 1A: Tactical Cumulative Return Curve vs. JGP Hurdle Rate
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📊 Gráfico 1A - Curva de Retorno Acumulado Tático (16 Semanas / 80 Pregões)")

    fig_cum = go.Figure()

    for ticker in avail_tickers:
        series = cum_returns[ticker]
        y_vals = (1.0 + series) * 100.0 if normalizer_base == "Base 100" else series * 100.0
        line_width = 3.5 if ticker == "SPY" else 1.8
        
        fig_cum.add_trace(go.Scatter(
            x=cum_returns.index,
            y=y_vals,
            mode="lines",
            name=f"{ticker} ({config.ETF_NAMES.get(ticker, ticker)})",
            line=dict(width=line_width),
            hovertemplate=f"<b>{ticker}</b><br>Data: %{{x|%Y-%m-%d}}<br>Retorno: %{{y:.2f}}" + ("" if normalizer_base == "Base 100" else "%") + "<extra></extra>"
        ))

    # Add Hurdle Rate reference line
    if normalizer_base == "Base 100":
        hurdle_y = (1.0 + config.HURDLE_RATE_PRO_RATA) * 100.0
        y_title = "Valor Normalizado (Base 100)"
    else:
        hurdle_y = config.HURDLE_RATE_PRO_RATA * 100.0
        y_title = "Retorno Acumulado (%)"

    fig_cum.add_shape(
        type="line",
        x0=cum_returns.index[0],
        x1=cum_returns.index[-1],
        y0=hurdle_y,
        y1=hurdle_y,
        line=dict(color="#FFD700", width=2.5, dash="dash")
    )

    fig_cum.add_annotation(
        x=cum_returns.index[int(len(cum_returns) * 0.7)],
        y=hurdle_y,
        text="<b>JGP Hurdle Rate (+1.56% pro-rata / 5% a.a.)</b>",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#FFD700",
        font=dict(color="#FFD700", size=12)
    )

    fig_cum.update_layout(
        template="plotly_dark",
        height=520,
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(title="Período Tático", showgrid=True, gridcolor="#333333"),
        yaxis=dict(title=y_title, showgrid=True, gridcolor="#333333"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig_cum, use_container_width=True)

    # -------------------------------------------------------------------------
    # Expanded Feature 2: August to December Historical Seasonality (5 to 10 Years)
    # Uses FULL historical price dataset for 5-10 year window extraction!
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🍂 Módulo de Sazonalidade Homóloga (Janela de Agosto a Dezembro - 5 a 10 Anos)")
    st.caption("Filtro estatístico exclusivo extraindo os intervalos entre 01 de Agosto e 31 de Dezembro nos últimos 5 a 10 anos para avaliar o rali histórico de fim de ano.")

    col_seas1, col_seas2 = st.columns([2, 2])
    with col_seas1:
        years_history = st.radio(
            "Histórico de Anos Analisados",
            options=[5, 10],
            format_func=lambda x: f"Últimos {x} Anos",
            index=0,
            horizontal=True,
            key="tab1_seas_years"
        )

    # Use FULL prices dataset for seasonality calculation to ensure 5-10 year lookback works
    avail_full_tickers = [t for t in selected_tickers if t in full_prices_df.columns]
    
    df_seas_summary, df_seas_yearly = metrics.calculate_aug_dec_seasonality(
        full_prices_df[avail_full_tickers],
        years_lookback=years_history
    )

    if not df_seas_summary.empty:
        st.markdown("#### 🏆 Destaques da Janela Sazonal Ago-Dez")
        badge_cols = st.columns(min(6, len(df_seas_summary)))
        
        for idx, col_box in enumerate(badge_cols):
            row = df_seas_summary.iloc[idx]
            ticker = row["Ticker"]
            win_rate = row["Win Rate (%)"]
            mean_ret = row["Média Retorno Ago-Dez"] * 100.0
            
            b_color = "#00E676" if win_rate >= 80 else "#FFB300" if win_rate >= 50 else "#FF5252"
            
            col_box.markdown(f"""
            <div style="background-color: #1E222D; padding: 12px; border-radius: 8px; border-left: 4px solid {b_color}; text-align: center;">
                <h4 style="margin: 0; color: #FFFFFF;">{ticker}</h4>
                <p style="margin: 4px 0; font-size: 13px; color: #B2B9C0;">Win Rate: <b style="color:{b_color};">{win_rate:.0f}%</b></p>
                <p style="margin: 0; font-size: 12px; color: #808A9D;">Média: <b>{mean_ret:+.2f}%</b></p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart 1B: Aug-Dec Seasonality Bar Chart per ETF
        fig_seas_bar = go.Figure()
        
        fig_seas_bar.add_trace(go.Bar(
            x=df_seas_summary["Ticker"],
            y=df_seas_summary["Média Retorno Ago-Dez"] * 100.0,
            marker_color=["#00E676" if r >= 0 else "#FF5252" for r in df_seas_summary["Média Retorno Ago-Dez"]],
            text=df_seas_summary["Média Retorno Ago-Dez"].apply(lambda x: f"{x*100:+.2f}%"),
            textposition="outside",
            hovertemplate="<b>%{x}</b> (%{customdata})<br>Retorno Médio Ago-Dez: %{y:+.2f}%<extra></extra>",
            customdata=df_seas_summary["Nome"]
        ))

        fig_seas_bar.update_layout(
            template="plotly_dark",
            height=480,
            title=dict(text=f"Retorno Médio no Período Ago-Dez (Últimos {years_history} Anos)"),
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis=dict(title="ETFs Elegíveis", showgrid=False),
            yaxis=dict(title="Retorno Médio Acumulado (%)", showgrid=True, gridcolor="#333333")
        )

        st.plotly_chart(fig_seas_bar, use_container_width=True)

        # Sector Comparison
        st.markdown("#### ⚡ Comparativo Setorial: Cíclicos/Crescimento vs. Defensivos (Ago - Dez)")
        
        sector_seas_df = metrics.calculate_sector_group_seasonality(
            full_prices_df[avail_full_tickers],
            years_lookback=years_history
        )

        if not sector_seas_df.empty:
            c_sec1, c_sec2 = st.columns([3, 2])
            
            with c_sec1:
                fig_sec = go.Figure()
                fig_sec.add_trace(go.Bar(
                    x=sector_seas_df["Setor"],
                    y=sector_seas_df["Mean_Return"] * 100.0,
                    marker_color=["#2962FF" if "Cíclicos" in s else "#FF6D00" if "Defensivos" in s else "#78909C" for s in sector_seas_df["Setor"]],
                    text=sector_seas_df["Mean_Return"].apply(lambda x: f"{x*100:+.2f}%"),
                    textposition="auto"
                ))
                fig_sec.update_layout(
                    template="plotly_dark",
                    height=350,
                    title=dict(text="Retorno Médio Sazonal por Agrupamento Setorial"),
                    margin=dict(l=30, r=30, t=40, b=30),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(title="Retorno Médio (%)", showgrid=True, gridcolor="#333333")
                )
                st.plotly_chart(fig_sec, use_container_width=True)
                
            with c_sec2:
                st.markdown("##### Resumo do Rali por Categoria")
                for _, r_sec in sector_seas_df.iterrows():
                    st.metric(
                        label=r_sec["Setor"],
                        value=f"{r_sec['Mean_Return']*100:+.2f}%",
                        delta=f"Win Rate Médio: {r_sec['Average_Win_Rate']:.0f}%"
                    )

        # Table detailing Year-by-Year Aug-Dec performance
        with st.expander("📄 Ver Matriz Detalhada Ano a Ano (01/Ago a 31/Dez)"):
            disp_y = df_seas_yearly.copy()
            year_cols = [c for c in disp_y.columns if c not in ["Ticker", "Setor"]]
            for col in year_cols:
                disp_y[col] = disp_y[col].apply(lambda x: f"{x*100:+.2f}%" if pd.notnull(x) else "-")
            st.dataframe(disp_y, use_container_width=True)
    else:
        st.info("Carregando estatísticas históricas de sazonalidade...")
