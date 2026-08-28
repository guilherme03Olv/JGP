"""
tab3_holdings.py - Tab 3: Top 10 Holdings Decomposition, CR10 & HHI Concentration Metrics
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import config
import metrics


def render_tab3():
    st.markdown("## 🔍 Módulo 3: Decomposição dos Top 10 Holdings & Risco de Concentração")
    st.caption("Diagnóstico da estrutura interna dos ETFs para separar risco idiossincrático de poucas ações dominantes de exposições beta setoriais amplas.")

    # Selector for target ETF
    col_sel1, col_sel2 = st.columns([2, 2])
    with col_sel1:
        selected_etf = st.selectbox(
            "Selecionar ETF para Decomposição Estrutural",
            options=config.ALL_ETFS,
            index=config.ALL_ETFS.index("EWZ") if "EWZ" in config.ALL_ETFS else 0,
            key="tab3_etf_select"
        )
    with col_sel2:
        chart_type = st.radio(
            "Visualização dos Componentes",
            options=["Gráfico de Barras Horizontal", "Treemap Proporcional"],
            index=0,
            horizontal=True,
            key="tab3_chart_type"
        )

    # Fetch holdings data from config or default fallback
    holdings = config.ETF_TOP10_HOLDINGS.get(selected_etf, config.DEFAULT_GENERIC_HOLDINGS)
    
    # Calculate CR10 and HHI
    metrics_res = metrics.calculate_cr10_and_hhi(holdings)
    cr10_val = metrics_res["CR10"]
    hhi_val = metrics_res["HHI"]
    hhi_cat = metrics_res["HHI_Category"]
    hhi_badge = metrics_res["HHI_Badge"]

    # -------------------------------------------------------------------------
    # Diagnostic Risk Cards & Badges
    # -------------------------------------------------------------------------
    st.markdown("---")
    c_card1, c_card2, c_card3 = st.columns(3)

    badge_color = "#00E676" if hhi_badge == "success" else "#FFB300" if hhi_badge == "warning" else "#FF5252"

    c_card1.markdown(f"""
    <div style="background-color: #1E222D; padding: 16px; border-radius: 10px; border-top: 4px solid #2962FF; text-align: center;">
        <h4 style="margin: 0; color: #808A9D; font-size: 13px;">TAXA DE CONCENTRAÇÃO (CR10)</h4>
        <h2 style="margin: 8px 0; color: #FFFFFF; font-size: 28px;">{cr10_val:.1f}%</h2>
        <p style="margin: 0; font-size: 12px; color: #B2B9C0;">Peso dos 10 maiores componentes</p>
    </div>
    """, unsafe_allow_html=True)

    c_card2.markdown(f"""
    <div style="background-color: #1E222D; padding: 16px; border-radius: 10px; border-top: 4px solid {badge_color}; text-align: center;">
        <h4 style="margin: 0; color: #808A9D; font-size: 13px;">ÍNDICE HERFINDAHL-HIRSCHMAN (HHI)</h4>
        <h2 style="margin: 8px 0; color: {badge_color}; font-size: 28px;">{hhi_val:.0f}</h2>
        <p style="margin: 0; font-size: 12px; color: #B2B9C0;">Status: <b style="color: {badge_color};">{hhi_cat}</b></p>
    </div>
    """, unsafe_allow_html=True)

    c_card3.markdown(f"""
    <div style="background-color: #1E222D; padding: 16px; border-radius: 10px; border-top: 4px solid #9C27B0; text-align: center;">
        <h4 style="margin: 0; color: #808A9D; font-size: 13px;">ALERTA DE SENSIBILIDADE</h4>
        <h3 style="margin: 8px 0; color: #FFFFFF; font-size: 20px;">{"Alta" if hhi_val > 1800 else "Moderada" if hhi_val >= 1000 else "Baixa"}</h3>
        <p style="margin: 0; font-size: 12px; color: #B2B9C0;">Risco idiossincrático de balanços</p>
    </div>
    """, unsafe_allow_html=True)

    # Prepare DataFrame for Holdings breakdown
    df_holdings = pd.DataFrame(holdings, columns=["Ticker", "Empresa", "Peso (%)"])
    other_weight = max(0.0, 100.0 - cr10_val)
    
    df_chart = pd.concat([
        df_holdings,
        pd.DataFrame([{"Ticker": "DEMAIS", "Empresa": "Demais Ativos da Carteira", "Peso (%)": other_weight}])
    ], ignore_index=True)

    # -------------------------------------------------------------------------
    # Chart 3A: Holdings Decomposition (Bar / Treemap)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown(f"### 📊 Decomposição dos Ativos de **{selected_etf}** ({config.ETF_NAMES.get(selected_etf, '')})")

    if chart_type == "Gráfico de Barras Horizontal":
        fig_hold = go.Figure()
        
        # Colors: Top 10 in cyan/blue, Demais in gray
        colors = ["#00E5FF" if t != "DEMAIS" else "#455A64" for t in df_chart["Ticker"]]
        
        fig_hold.add_trace(go.Bar(
            y=df_chart["Ticker"] + " - " + df_chart["Empresa"],
            x=df_chart["Peso (%)"],
            orientation="h",
            marker=dict(color=colors),
            text=df_chart["Peso (%)"].apply(lambda x: f"{x:.2f}%"),
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Peso: %{x:.2f}%<extra></extra>"
        ))
        
        fig_hold.update_layout(
            template="plotly_dark",
            height=500,
            margin=dict(l=50, r=40, t=30, b=40),
            xaxis=dict(title="Peso Percentual (%)", showgrid=True, gridcolor="#333333"),
            yaxis=dict(autorange="reversed", showgrid=False)
        )
        st.plotly_chart(fig_hold, use_container_width=True)

    else:
        # Treemap
        fig_tree = px.treemap(
            df_chart,
            path=["Empresa"],
            values="Peso (%)",
            color="Peso (%)",
            color_continuous_scale="Blues",
            title=f"Treemap Proporcional de Holdings - {selected_etf}"
        )
        fig_tree.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig_tree, use_container_width=True)

    # -------------------------------------------------------------------------
    # Chart 3B: CR10 Concentration Ranking Across All 18 ETFs
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🏆 Ranking Comparativo de Concentração (CR10) dos 18 ETFs")

    ranking_records = []
    for etf in config.ALL_ETFS:
        h_data = config.ETF_TOP10_HOLDINGS.get(etf, config.DEFAULT_GENERIC_HOLDINGS)
        m = metrics.calculate_cr10_and_hhi(h_data)
        ranking_records.append({
            "ETF": etf,
            "Nome": config.ETF_NAMES.get(etf, etf),
            "CR10 (%)": m["CR10"],
            "HHI": m["HHI"],
            "Categoria": m["HHI_Category"]
        })

    df_rank = pd.DataFrame(ranking_records).sort_values(by="CR10 (%)", ascending=False)

    fig_rank = go.Figure()
    fig_rank.add_trace(go.Bar(
        x=df_rank["ETF"],
        y=df_rank["CR10 (%)"],
        marker_color=["#FF5252" if h > 1800 else "#FFB300" if h >= 1000 else "#00E676" for h in df_rank["HHI"]],
        text=df_rank["CR10 (%)"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{x}</b> (%{customdata})<br>CR10: %{y:.1f}%<extra></extra>",
        customdata=df_rank["Nome"]
    ))

    fig_rank.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=40, r=40, t=30, b=40),
        xaxis=dict(title="ETFs Elegíveis", showgrid=False),
        yaxis=dict(title="Taxa CR10 (%)", range=[0, 115], showgrid=True, gridcolor="#333333")
    )

    st.plotly_chart(fig_rank, use_container_width=True)
