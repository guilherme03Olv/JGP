"""
tab6_elections.py - Tab 6: Brazil Election Cycles (2010, 2014, 2018, 2022) - EWZ Top Holdings & Political Spread
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import config
import metrics
import data_loader


def render_tab6():
    st.markdown("## 🇧🇷 Módulo 6: Ciclos Eleitorais no Brasil (2010, 2014, 2018, 2022) & Top Holdings do EWZ")
    st.caption("Análise quantitativa do comportamento das 4 cestas temáticas do EWZ (Estatais, Financeiro Privado, Exportadoras, Consumo) durante o período eleitoral presidencial (Setembro a Dezembro).")

    # Select Election Year
    col_e1, col_e2 = st.columns([2, 2])
    with col_e1:
        selected_year = st.selectbox(
            "Selecionar Ano Eleitoral Presidencial",
            options=config.ELECTION_YEARS,
            index=config.ELECTION_YEARS.index(2022),
            key="tab6_year_select"
        )
    with col_e2:
        st.info("ℹ️ Período Analisado: 1º de Setembro a 31 de Dezembro (16 semanas / ~80 pregões úteis)")

    # Fetch election period data for selected year
    b3_prices = data_loader.fetch_election_year_data(config.ALL_B3_TICKERS, selected_year)

    if b3_prices.empty:
        st.warning(f"Dados indisponíveis para o ano eleitoral de {selected_year}.")
        return

    # -------------------------------------------------------------------------
    # Chart 6A: Return Matrix of Top Holdings Across Election Years
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown(f"### 📊 Gráfico 6A - Matriz de Retorno dos Top Holdings no Período Eleitoral ({selected_year})")

    # Calculate individual returns for the period
    period_returns = (b3_prices.iloc[-1] / b3_prices.iloc[0]) - 1.0
    
    # Calculate 20d volatility for each ticker in period
    daily_rets = np.log(b3_prices / b3_prices.shift(1)).dropna()
    vols_20d_period = daily_rets.tail(20).std() * config.VOL_ANNUALIZATION_FACTOR * 100.0

    df_holdings_res = pd.DataFrame({
        "Ticker": period_returns.index,
        "Empresa": [config.B3_TICKER_NAMES.get(f"{t}.SA", t) for t in period_returns.index],
        "Retorno Q4 (%)": period_returns.values * 100.0,
        "Volatilidade 20d (%)": vols_20d_period.values
    }).sort_values(by="Retorno Q4 (%)", ascending=False)

    fig_matrix = go.Figure()
    fig_matrix.add_trace(go.Bar(
        x=df_holdings_res["Ticker"],
        y=df_holdings_res["Retorno Q4 (%)"],
        marker_color=["#00E676" if r >= 0 else "#FF5252" for r in df_holdings_res["Retorno Q4 (%)"]],
        text=df_holdings_res["Retorno Q4 (%)"].apply(lambda x: f"{x:+.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Empresa: %{customdata}<br>Retorno Q4: %{y:+.2f}%<extra></extra>",
        customdata=df_holdings_res["Empresa"]
    ))

    fig_matrix.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=40, r=40, t=30, b=40),
        xaxis=dict(title="Ações Subjacentes do EWZ", showgrid=False),
        yaxis=dict(title="Retorno no Período Eleitoral (%)", showgrid=True, gridcolor="#333333")
    )
    st.plotly_chart(fig_matrix, use_container_width=True)

    # -------------------------------------------------------------------------
    # Chart 6B: Cumulative Performance by Theme Basket (Base 100)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown(f"### 📈 Gráfico 6B - Performance Acumulada Média por Cesta Temática (Base 100 - {selected_year})")
    st.caption("Linhas verticais demarcam o 1º e 2º Turnos das eleições presidenciais no Brasil.")

    basket_perf = metrics.calculate_basket_performance(b3_prices)

    fig_basket = go.Figure()

    colors_baskets = {
        "Estatais": "#FF5252",                # Red for political risk
        "Financeiro Privado": "#2962FF",       # Blue for institutional resilience
        "Commodities / Exportadoras": "#FFD700", # Gold for commodities
        "Consumo Doméstico / Indústria": "#00E676" # Green for domestic consumption
    }

    for basket_col in basket_perf.columns:
        fig_basket.add_trace(go.Scatter(
            x=basket_perf.index,
            y=basket_perf[basket_col],
            mode="lines",
            name=basket_col,
            line=dict(color=colors_baskets.get(basket_col, "#FFFFFF"), width=2.5)
        ))

    # Determine approximate 1st and 2nd round election dates for chosen year
    election_dates_map = {
        2010: ("2010-10-03", "2010-10-31"),
        2014: ("2014-10-05", "2014-10-26"),
        2018: ("2018-10-07", "2018-10-28"),
        2022: ("2022-10-02", "2022-10-30")
    }
    dt_1st, dt_2nd = election_dates_map.get(selected_year, (f"{selected_year}-10-02", f"{selected_year}-10-30"))

    # Add vertical lines for 1st and 2nd turns
    fig_basket.add_vline(x=dt_1st, line_width=2, line_dash="dash", line_color="#FF9800", annotation_text="1º Turno", annotation_position="top left")
    fig_basket.add_vline(x=dt_2nd, line_width=2, line_dash="dash", line_color="#E040FB", annotation_text="2º Turno", annotation_position="top right")

    fig_basket.update_layout(
        template="plotly_dark",
        height=480,
        margin=dict(l=40, r=40, t=30, b=40),
        xaxis=dict(title="Data (Setembro a Dezembro)", showgrid=True, gridcolor="#333333"),
        yaxis=dict(title="Performance Normalizada (Base 100)", showgrid=True, gridcolor="#333333"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_basket, use_container_width=True)

    # -------------------------------------------------------------------------
    # Chart 6C: Political Risk Spread & Post-Election Volatility Compression
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### ⚖️ Gráfico 6C - Spread de Risco Político & Volatilidade (Pré vs. Pós-Eleição)")

    col_pol1, col_pol2 = st.columns([2, 2])

    with col_pol1:
        st.markdown("#### Spread Risco Político: (PETR4 + BBAS3)/2 vs. (ITUB4 + BBDC4)/2")
        pol_spread = metrics.calculate_political_risk_spread(b3_prices)
        
        if not pol_spread.empty:
            fig_spread = go.Figure()
            fig_spread.add_trace(go.Scatter(
                x=pol_spread.index,
                y=pol_spread * 100.0,
                mode="lines",
                name="Spread Estatais vs. Privadas",
                line=dict(color="#FF6D00", width=2.0),
                fill="tozeroy",
                fillcolor="rgba(255, 109, 0, 0.15)"
            ))
            fig_spread.update_layout(
                template="plotly_dark",
                height=380,
                margin=dict(l=30, r=30, t=20, b=30),
                xaxis=dict(showgrid=True, gridcolor="#333333"),
                yaxis=dict(title="Spread Acumulado (%)", showgrid=True, gridcolor="#333333")
            )
            st.plotly_chart(fig_spread, use_container_width=True)

    with col_pol2:
        st.markdown("#### Compressão de Volatilidade 20d (Pré 1º Turno vs. Pós 2º Turno)")
        vol_comp = metrics.calculate_volatility_compression(b3_prices, election_date=dt_2nd)
        
        if not vol_comp.empty:
            fig_vol_comp = go.Figure()
            fig_vol_comp.add_trace(go.Bar(
                x=vol_comp["Ticker"],
                y=vol_comp["Compressão / Choque (pp)"],
                marker_color=["#00E676" if x < 0 else "#FF5252" for x in vol_comp["Compressão / Choque (pp)"]],
                text=vol_comp["Compressão / Choque (pp)"].apply(lambda x: f"{x:+.1f}pp" if pd.notnull(x) else ""),
                textposition="outside"
            ))
            fig_vol_comp.update_layout(
                template="plotly_dark",
                height=380,
                margin=dict(l=30, r=30, t=20, b=30),
                xaxis=dict(showgrid=False),
                yaxis=dict(title="Variação de Volatilidade 20d (pp)", showgrid=True, gridcolor="#333333")
            )
            st.plotly_chart(fig_vol_comp, use_container_width=True)
