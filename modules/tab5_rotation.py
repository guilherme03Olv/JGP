"""
tab5_rotation.py - Tab 5: Sector Rotation, Relative Strength, RRG 2D, Drawdown & JGP Markowitz Frontier
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import config
import metrics


def render_tab5(prices_df: pd.DataFrame):
    st.markdown("## 🔄 Módulo 5: Rotação Setorial, RRG 2D, Drawdown & Fronteira de Markowitz JGP")
    st.caption("Mapeamento da liderança de momentum setorial relativo ao S&P 500 (SPY), quantificação do Worst Drawdown e otimização de portfólio sob restrição de capital não-alavancado (∑|w_i| ≤ 1.0).")

    if prices_df.empty or "SPY" not in prices_df.columns:
        st.error("Dados insuficientes ou ausência do benchmark SPY para processar o Módulo 5.")
        return

    # -------------------------------------------------------------------------
    # Chart 5A: Relative Strength Ratio vs. SPY
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📊 Gráfico 5A - Ratio de Força Relativa (Relative Strength vs. SPY)")

    col_rs1, col_rs2 = st.columns([2, 2])
    with col_rs1:
        rs_etf = st.selectbox(
            "Selecionar ETF para Análise de Força Relativa",
            options=[c for c in prices_df.columns if c != "SPY"],
            index=0,
            key="tab5_rs_etf"
        )

    rs_df = metrics.calculate_relative_strength(prices_df, benchmark_ticker="SPY")
    
    if rs_etf in rs_df.columns:
        series_rs = rs_df[rs_etf].dropna()
        sma50_rs = series_rs.rolling(50).mean()
        sma200_rs = series_rs.rolling(200).mean()

        fig_rs = go.Figure()
        fig_rs.add_trace(go.Scatter(
            x=series_rs.index, y=series_rs,
            mode="lines", name=f"Ratio {rs_etf}/SPY",
            line=dict(color="#00E5FF", width=2.0)
        ))
        fig_rs.add_trace(go.Scatter(
            x=sma50_rs.index, y=sma50_rs,
            mode="lines", name="SMA 50 (Ratio)",
            line=dict(color="#FFEA00", width=1.5)
        ))
        fig_rs.add_trace(go.Scatter(
            x=sma200_rs.index, y=sma200_rs,
            mode="lines", name="SMA 200 (Ratio)",
            line=dict(color="#E040FB", width=1.5)
        ))

        fig_rs.update_layout(
            template="plotly_dark",
            height=420,
            margin=dict(l=40, r=40, t=30, b=40),
            title=dict(text=f"Razão de Desempenho Relativo: <b>{rs_etf}</b> / <b>SPY</b>"),
            xaxis=dict(showgrid=True, gridcolor="#333333"),
            yaxis=dict(title="Força Relativa (RS)", showgrid=True, gridcolor="#333333"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_rs, use_container_width=True)

    # -------------------------------------------------------------------------
    # Chart 5B: Relative Rotation Graph (RRG 2D)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🌀 Gráfico 5B - Quadrantes RRG (Relative Rotation Graph 2D)")
    st.caption("Visualização 2D de liderança e rotação de momentum: Leading (Verde), Weakening (Amarelo), Lagging (Vermelho), Improving (Azul).")

    rrg_df = metrics.calculate_rrg_metrics(prices_df, benchmark_ticker="SPY", lookback=14)

    if not rrg_df.empty:
        color_map = {
            "Leading": "#00E676",
            "Weakening": "#FFD600",
            "Lagging": "#FF5252",
            "Improving": "#29B6F6"
        }

        fig_rrg = go.Figure()

        # Add 4 Quadrant Background Shapes
        fig_rrg.add_shape(type="rect", x0=100, x1=115, y0=100, y1=115, fillcolor="rgba(0,230,118,0.08)", line_width=0) # Leading
        fig_rrg.add_shape(type="rect", x0=100, x1=115, y0=85, y1=100, fillcolor="rgba(255,214,0,0.08)", line_width=0)  # Weakening
        fig_rrg.add_shape(type="rect", x0=85, x1=100, y0=85, y1=100, fillcolor="rgba(255,82,82,0.08)", line_width=0)   # Lagging
        fig_rrg.add_shape(type="rect", x0=85, x1=100, y0=100, y1=115, fillcolor="rgba(41,182,246,0.08)", line_width=0) # Improving

        # Add Axes Cross lines at 100, 100
        fig_rrg.add_shape(type="line", x0=85, x1=115, y0=100, y1=100, line=dict(color="#FFFFFF", width=1, dash="dash"))
        fig_rrg.add_shape(type="line", x0=100, x1=100, y0=85, y1=115, line=dict(color="#FFFFFF", width=1, dash="dash"))

        # Scatter points for assets
        for quad in ["Leading", "Weakening", "Lagging", "Improving"]:
            sub_q = rrg_df[rrg_df["Quadrant"] == quad]
            if not sub_q.empty:
                fig_rrg.add_trace(go.Scatter(
                    x=sub_q["RS-Ratio"],
                    y=sub_q["RS-Momentum"],
                    mode="markers+text",
                    name=quad,
                    text=sub_q["Ticker"],
                    textposition="top center",
                    marker=dict(size=12, color=color_map[quad]),
                    hovertemplate="<b>%{text}</b><br>RS-Ratio: %{x:.2f}<br>RS-Momentum: %{y:.2f}<br>Quadrante: " + quad + "<extra></extra>"
                ))

        fig_rrg.update_layout(
            template="plotly_dark",
            height=500,
            margin=dict(l=40, r=40, t=30, b=40),
            xaxis=dict(title="RS-Ratio (Tendência)", range=[90, 110], showgrid=True, gridcolor="#333333"),
            yaxis=dict(title="RS-Momentum (Impulso)", range=[90, 110], showgrid=True, gridcolor="#333333"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_rrg, use_container_width=True)

    # -------------------------------------------------------------------------
    # Chart 5C: Drawdown Underwater Chart
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🌊 Gráfico 5C - Painel de Drawdown (Underwater Chart)")

    dd_etf = st.selectbox(
        "Selecionar ETF para Análise de Drawdown",
        options=list(prices_df.columns),
        index=0,
        key="tab5_dd_etf"
    )

    drawdowns = metrics.calculate_drawdowns(prices_df[[dd_etf]])
    worst_dd = drawdowns[dd_etf].min() * 100.0

    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=drawdowns.index,
        y=drawdowns[dd_etf] * 100.0,
        mode="lines",
        name=f"Drawdown {dd_etf}",
        fill="tozeroy",
        fillcolor="rgba(255, 82, 82, 0.3)",
        line=dict(color="#FF5252", width=1.5),
        hovertemplate="<b>Data: %{x|%Y-%m-%d}</b><br>Drawdown: %{y:.2f}%<extra></extra>"
    ))

    fig_dd.update_layout(
        template="plotly_dark",
        height=380,
        margin=dict(l=40, r=40, t=30, b=40),
        title=dict(text=f"Drawdown Histórico de <b>{dd_etf}</b> (Worst DD: <b style='color:#FF5252;'>{worst_dd:.2f}%</b>)"),
        xaxis=dict(showgrid=True, gridcolor="#333333"),
        yaxis=dict(title="Queda a partir do Topo (%)", showgrid=True, gridcolor="#333333")
    )
    st.plotly_chart(fig_dd, use_container_width=True)

    # -------------------------------------------------------------------------
    # Chart 5D: JGP Markowitz Efficient Frontier Optimization
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🎯 Gráfico 5D - Fronteira Eficiente de Markowitz (Restrição JGP ∑|w_i| ≤ 1.0)")
    st.caption("Otimização Média-Variância sem alavancagem com inclusão do Hurdle Rate (5.0% a.a.) para identificação da Carteira Tangente de Máximo Sharpe.")

    # Compute expected returns (annualized) and covariance matrix
    daily_returns = np.log(prices_df / prices_df.shift(1)).dropna()
    exp_returns = daily_returns.mean() * config.TRADING_DAYS_PER_YEAR
    cov_matrix = daily_returns.cov()

    # Calculate 20d volatility for each asset
    vols_20d = daily_returns.tail(20).std() * config.VOL_ANNUALIZATION_FACTOR

    # Generate target returns array for frontier
    min_ret = exp_returns.min()
    max_ret = exp_returns.max()
    target_returns = np.linspace(min_ret, max_ret, 30)

    # Calculate Efficient Frontier
    f_vols, f_rets, f_weights = metrics.optimize_markowitz_jgp(
        exp_returns, cov_matrix, target_returns, max_capital_constraint=1.0
    )

    fig_ef = go.Figure()

    # Add Individual Assets Scatter
    fig_ef.add_trace(go.Scatter(
        x=vols_20d.values * 100.0,
        y=exp_returns.values * 100.0,
        mode="markers+text",
        name="ETFs Individuais",
        text=list(prices_df.columns),
        textposition="top center",
        marker=dict(size=10, color="#2962FF"),
        hovertemplate="<b>%{text}</b><br>Volatilidade 20d: %{x:.2f}%<br>Retorno Esperado: %{y:.2f}%<extra></extra>"
    ))

    # Add Efficient Frontier Curve
    if len(f_vols) > 0:
        fig_ef.add_trace(go.Scatter(
            x=f_vols * 100.0,
            y=f_rets * 100.0,
            mode="lines",
            name="Fronteira Eficiente JGP (Não Alavancada)",
            line=dict(color="#00E676", width=3.0)
        ))

        # Find Max Sharpe Portfolio on Frontier (Rf = 5.0%)
        rf_annual = config.HURDLE_RATE_ANNUAL * 100.0
        sharpe_ratios = (f_rets * 100.0 - rf_annual) / (f_vols * 100.0)
        max_idx = np.argmax(sharpe_ratios)
        
        opt_vol = f_vols[max_idx] * 100.0
        opt_ret = f_rets[max_idx] * 100.0
        opt_sharpe = sharpe_ratios[max_idx]
        opt_weights = f_weights[max_idx]

        # Highlight Optimal Sharpe Portfolio
        fig_ef.add_trace(go.Scatter(
            x=[opt_vol],
            y=[opt_ret],
            mode="markers+text",
            name="Carteira Tangente (Max Sharpe)",
            text=[f"<b>MAX SHARPE ({opt_sharpe:.2f})</b>"],
            textposition="top right",
            marker=dict(size=16, color="#FFD700", symbol="star"),
            hovertemplate=f"<b>Carteira Tangente JGP</b><br>Volatilidade: {opt_vol:.2f}%<br>Retorno Esperado: {opt_ret:.2f}%<br>Sharpe Ratio: {opt_sharpe:.2f}<extra></extra>"
        ))

    fig_ef.update_layout(
        template="plotly_dark",
        height=520,
        margin=dict(l=40, r=40, t=30, b=40),
        xaxis=dict(title="Volatilidade Anualizada 20d (%)", showgrid=True, gridcolor="#333333"),
        yaxis=dict(title="Retorno Esperado Anualizado (%)", showgrid=True, gridcolor="#333333"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig_ef, use_container_width=True)

    # Display Optimal Weights Table
    if len(f_vols) > 0:
        with st.expander("💼 Ver Alocação de Pesos da Carteira Tangente de Máximo Sharpe"):
            df_opt_w = pd.DataFrame({
                "ETF": list(prices_df.columns),
                "Nome": [config.ETF_NAMES.get(t, t) for t in prices_df.columns],
                "Peso Sugerido (%)": np.around(opt_weights * 100.0, 2)
            }).sort_values(by="Peso Sugerido (%)", ascending=False)
            
            st.dataframe(df_opt_w[df_opt_w["Peso Sugerido (%)"] > 0.01], use_container_width=True)
