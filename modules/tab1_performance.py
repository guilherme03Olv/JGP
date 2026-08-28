"""
tab1_performance.py - Tab 1: Tactical Performance vs. JGP Hurdle Rate (5% p.a.) & Q4 Seasonality
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import config
import metrics


def render_tab1(prices_df: pd.DataFrame):
    st.markdown("## 📈 Módulo 1: Performance Tática vs. Hurdle Rate & Sazonalidade Q4")
    st.caption("Identificação de alfa real sobre o custo do caixa JGP (5.0% a.a. / +1.56% no período de 16 semanas) e análise de sazonalidade histórica em Q4.")

    if prices_df.empty:
        st.error("Dados de preços não disponíveis para processamento do Módulo 1.")
        return

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

    # Filter selected tickers based on category selection
    selected_tickers = []
    for cat in category_filter:
        selected_tickers.extend(config.ETF_CATEGORIES[cat])
    selected_tickers = list(dict.fromkeys(selected_tickers)) # remove duplicates keeping order
    
    # Filter prices DataFrame
    avail_tickers = [t for t in selected_tickers if t in prices_df.columns]
    if not avail_tickers:
        st.warning("Nenhum ativo selecionado disponível nos dados.")
        return
        
    sub_prices = prices_df[avail_tickers]

    # Calculate returns according to Long or Short strategy
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

    # Base 100 or Percentage
    for ticker in avail_tickers:
        series = cum_returns[ticker]
        if normalizer_base == "Base 100":
            y_vals = (1.0 + series) * 100.0
        else:
            y_vals = series * 100.0

        # Highlight SPY benchmark with distinct thick line
        line_width = 3.5 if ticker == "SPY" else 1.8
        dash_style = "solid"
        
        fig_cum.add_trace(go.Scatter(
            x=cum_returns.index,
            y=y_vals,
            mode="lines",
            name=f"{ticker} ({config.ETF_NAMES.get(ticker, ticker)})",
            line=dict(width=line_width, dash=dash_style),
            hovertemplate=f"<b>{ticker}</b><br>Data: %{{x|%Y-%m-%d}}<br>Retorno: %{{y:.2f}}" + ("" if normalizer_base == "Base 100" else "%") + "<extra></extra>"
        ))

    # Add JGP Hurdle Rate (+1.56% pro rata) horizontal reference line
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
        line=dict(color="#FFD700", width=2.5, dash="dash"),
        name="JGP Hurdle Rate (+1.56%)"
    )

    fig_cum.add_annotation(
        x=cum_returns.index[int(len(cum_returns) * 0.7)],
        y=hurdle_y,
        text=f"<b>JGP Hurdle Rate (+1.56% pro-rata / 5% a.a.)</b>",
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
    # Chart 1B: Q4 Historical Seasonality & Win Rate
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🍂 Gráfico 1B - Sazonalidade Q4 Histórica (Últimos 4 Anos)")
    st.caption("Distribuição estatística dos retornos obtidos na janela tática de 16 semanas (Set-Dez) com badges de Win Rate sobre o Hurdle Rate.")

    seasonality_df = metrics.calculate_q4_seasonality(prices_df[avail_tickers])

    if not seasonality_df.empty:
        # Display Summary Cards & Badges for top assets
        st.markdown("#### 🏆 Destaques de Sazonalidade & Win Rate")
        badge_cols = st.columns(min(6, len(seasonality_df)))
        
        for idx, col_box in enumerate(badge_cols):
            row = seasonality_df.iloc[idx]
            ticker = row["Ticker"]
            win_rate = row["Win Rate (%)"]
            mean_ret = row["Mean Q4 Return"] * 100.0
            
            badge_color = "#00E676" if win_rate >= 75 else "#FFB300" if win_rate >= 50 else "#FF5252"
            
            col_box.markdown(f"""
            <div style="background-color: #1E222D; padding: 12px; border-radius: 8px; border-left: 4px solid {badge_color}; text-align: center;">
                <h4 style="margin: 0; color: #FFFFFF;">{ticker}</h4>
                <p style="margin: 4px 0; font-size: 13px; color: #B2B9C0;">Win Rate: <b style="color:{badge_color};">{win_rate:.0f}%</b></p>
                <p style="margin: 0; font-size: 12px; color: #808A9D;">Média Q4: <b>{mean_ret:+.2f}%</b></p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Plotly Bar Chart + Boxplot for Seasonality
        fig_seas = go.Figure()

        # Add Bars for Mean Return
        fig_seas.add_trace(go.Bar(
            x=seasonality_df["Ticker"],
            y=seasonality_df["Mean Q4 Return"] * 100.0,
            name="Retorno Médio Q4 (%)",
            marker_color="#2962FF",
            hovertemplate="<b>%{x}</b><br>Retorno Médio: %{y:.2f}%<extra></extra>"
        ))

        # Add Boxplot trace for return distribution
        q4_years_cols = [c for c in seasonality_df.columns if c.startswith("Q4 ")]
        for _, r in seasonality_df.iterrows():
            vals = [r[c] * 100.0 for c in q4_years_cols if not np.isnan(r[c])]
            fig_seas.add_trace(go.Box(
                y=vals,
                name=r["Ticker"],
                boxpoints="all",
                jitter=0.3,
                pointpos=-1.8,
                showlegend=False,
                marker=dict(size=6, color="#FF6D00")
            ))

        # Add Hurdle Rate threshold line
        fig_seas.add_shape(
            type="line",
            x0=-0.5,
            x1=len(seasonality_df) - 0.5,
            y0=config.HURDLE_RATE_PRO_RATA * 100.0,
            y1=config.HURDLE_RATE_PRO_RATA * 100.0,
            line=dict(color="#FFD700", width=2, dash="dash")
        )

        fig_seas.update_layout(
            template="plotly_dark",
            height=480,
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis=dict(title="ETFs Elegíveis", showgrid=False),
            yaxis=dict(title="Retorno Q4 (%)", showgrid=True, gridcolor="#333333"),
            barmode="group"
        )

        st.plotly_chart(fig_seas, use_container_width=True)

        # Detailed Table View
        with st.expander("📄 Ver Tabela Detalhada de Retornos Sazonais por Ano"):
            disp_table = seasonality_df.copy()
            for col in disp_table.columns:
                if col != "Ticker" and "Win Rate" not in col:
                    disp_table[col] = disp_table[col].apply(lambda x: f"{x*100:+.2f}%" if pd.notnull(x) else "-")
                elif "Win Rate" in col:
                    disp_table[col] = disp_table[col].apply(lambda x: f"{x:.0f}%")
            st.dataframe(disp_table, use_container_width=True)
