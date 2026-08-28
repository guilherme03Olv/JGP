"""
metrics.py - Expanded Quantitative Calculation Engine & Mathematical Functions for JGP 2026 Dashboard
"""

import numpy as np
import pandas as pd
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
from scipy.optimize import minimize
from typing import Tuple, Dict, List, Optional
from datetime import datetime
import config


# -----------------------------------------------------------------------------
# Return Calculations
# -----------------------------------------------------------------------------
def calculate_daily_returns(prices: pd.DataFrame, log_returns: bool = False) -> pd.DataFrame:
    """Calculates daily simple or logarithmic returns."""
    if log_returns:
        return np.log(prices / prices.shift(1)).dropna()
    else:
        return prices.pct_change().dropna()


def calculate_cumulative_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculates cumulative tactical returns R_cum = prod(1 + r) - 1."""
    daily_returns = prices.pct_change().fillna(0)
    return (1.0 + daily_returns).cumprod() - 1.0


def calculate_short_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates net returns for short positions deducting JGP borrowing cost:
    r_short,t = -r_t - 0.004/20
    """
    daily_returns = prices.pct_change().fillna(0)
    daily_short = -daily_returns - config.SHORT_BORROWING_COST_DAILY
    return (1.0 + daily_short).cumprod() - 1.0


# -----------------------------------------------------------------------------
# Expanded Feature 2: August to December Historical Seasonality (5 to 10 Years)
# -----------------------------------------------------------------------------
def calculate_aug_dec_seasonality(
    prices: pd.DataFrame,
    years_lookback: int = 5
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extracts exclusively the intervals between 01 of August and 31 of December for each year
    over the last N years (5 to 10 years).
    
    Returns:
        1. Summary DataFrame (Ticker, Mean Aug-Dec Return, Median Return, Win Rate %, Sector Group)
        2. Yearly matrix DataFrame (Ticker x Year)
    """
    current_year = datetime.now().year
    start_year = current_year - years_lookback
    
    summary_records = []
    yearly_matrix_records = []
    
    for ticker in prices.columns:
        series = prices[ticker].dropna()
        if series.empty:
            continue
            
        yearly_rets = {}
        ret_vals = []
        
        for year in range(start_year, current_year):
            aug_start = f"{year}-08-01"
            dec_end = f"{year}-12-31"
            
            sub = series.loc[(series.index >= aug_start) & (series.index <= dec_end)]
            if len(sub) > 10:
                ret = (sub.iloc[-1] / sub.iloc[0]) - 1.0
                yearly_rets[f"{year}"] = ret
                ret_vals.append(ret)
            else:
                yearly_rets[f"{year}"] = np.nan
                
        if ret_vals:
            mean_ret = np.mean(ret_vals)
            median_ret = np.median(ret_vals)
            win_rate = np.mean([r > 0 for r in ret_vals]) * 100.0
            
            # Identify Sector Type
            sector_type = "Outros"
            for st_name, t_list in config.SECTOR_TYPES.items():
                if ticker in t_list:
                    sector_type = st_name
                    break
                    
            summary_records.append({
                "Ticker": ticker,
                "Nome": config.ETF_NAMES.get(ticker, ticker),
                "Setor": sector_type,
                "Média Retorno Ago-Dez": mean_ret,
                "Mediana Retorno": median_ret,
                "Win Rate (%)": win_rate,
                "Anos Avaliados": len(ret_vals)
            })
            
            y_rec = {"Ticker": ticker, "Setor": sector_type}
            y_rec.update(yearly_rets)
            yearly_matrix_records.append(y_rec)
            
    df_summary = pd.DataFrame(summary_records)
    if not df_summary.empty:
        df_summary = df_summary.sort_values(by="Média Retorno Ago-Dez", ascending=False).reset_index(drop=True)
        
    df_yearly = pd.DataFrame(yearly_matrix_records)
    return df_summary, df_yearly


def calculate_sector_group_seasonality(
    prices: pd.DataFrame,
    years_lookback: int = 5
) -> pd.DataFrame:
    """
    Compares average Aug-Dec performance between Cyclical/Growth vs Defensive sector baskets.
    """
    df_summary, _ = calculate_aug_dec_seasonality(prices, years_lookback)
    if df_summary.empty:
        return pd.DataFrame()
        
    group_summary = df_summary.groupby("Setor").agg(
        Mean_Return=("Média Retorno Ago-Dez", "mean"),
        Average_Win_Rate=("Win Rate (%)", "mean"),
        ETF_Count=("Ticker", "count")
    ).reset_index()
    
    return group_summary.sort_values(by="Mean_Return", ascending=False)


# -----------------------------------------------------------------------------
# Expanded Feature 3: Short-Term Rolling Metrics (20d Vol, 1M/21d & 3M/63d Returns)
# -----------------------------------------------------------------------------
def calculate_short_term_metrics(prices_series: pd.Series) -> Dict:
    """
    Calculates short-term tactical metrics:
    - 20d Rolling Volatility Annualized (std_20d * sqrt(252))
    - 1 Month Return (21 trading days)
    - 3 Months Return (63 trading days)
    - Historical Mean Volatility
    - Volatility Regime Classification
    """
    s_clean = prices_series.dropna()
    if len(s_clean) < 64:
        return {}
        
    log_returns = np.log(s_clean / s_clean.shift(1)).dropna()
    roll_vol_20d = log_returns.rolling(window=config.VOL_WINDOW_JGP).std() * config.VOL_ANNUALIZATION_FACTOR * 100.0
    
    curr_vol = roll_vol_20d.iloc[-1]
    hist_mean_vol = roll_vol_20d.mean()
    hist_std_vol = roll_vol_20d.std()
    
    # 1 Month (21d) and 3 Months (63d) returns
    ret_1m = (s_clean.iloc[-1] / s_clean.iloc[-config.SHORT_TERM_1M_DAYS - 1]) - 1.0 if len(s_clean) > config.SHORT_TERM_1M_DAYS else 0.0
    ret_3m = (s_clean.iloc[-1] / s_clean.iloc[-config.SHORT_TERM_3M_DAYS - 1]) - 1.0 if len(s_clean) > config.SHORT_TERM_3M_DAYS else 0.0
    
    # Volatility Regime Classification
    if curr_vol < 12.0:
        regime = "Baixa Volatilidade (< 12%)"
        regime_badge = "success"
    elif curr_vol <= 22.0:
        regime = "Volatilidade Moderada (12% - 22%)"
        regime_badge = "warning"
    else:
        regime = "Elevada Volatilidade (> 22%)"
        regime_badge = "danger"
        
    return {
        "Current_Vol_20d": curr_vol,
        "Hist_Mean_Vol": hist_mean_vol,
        "Vol_Delta_Vs_Mean": curr_vol - hist_mean_vol,
        "Ret_1M_21d": ret_1m * 100.0,
        "Ret_3M_63d": ret_3m * 100.0,
        "Regime": regime,
        "Regime_Badge": regime_badge,
        "Roll_Vol_Series": roll_vol_20d
    }


# -----------------------------------------------------------------------------
# Module 2: Correlation Matrix & Ward Clustering
# -----------------------------------------------------------------------------
def calculate_correlation_matrix(prices: pd.DataFrame, window: Optional[int] = None) -> pd.DataFrame:
    """Calculates Pearson correlation matrix on daily log returns for specified lookback window."""
    log_ret = np.log(prices / prices.shift(1)).dropna()
    if window and len(log_ret) > window:
        log_ret = log_ret.tail(window)
    return log_ret.corr(method="pearson")


def perform_ward_clustering(corr_matrix: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Performs Ward's linkage hierarchical clustering on correlation matrix using
    Euclidean distance d_ij = sqrt(2 * (1 - rho_ij)).
    """
    corr_clipped = np.clip(corr_matrix.values, -1.0, 1.0)
    dist_matrix = np.sqrt(2.0 * (1.0 - corr_clipped))
    
    condensed_dist = squareform(dist_matrix, checks=False)
    linkage_matrix = hierarchy.linkage(condensed_dist, method="ward")
    
    dendro = hierarchy.dendrogram(linkage_matrix, no_plot=True)
    order = dendro["leaves"]
    
    reordered_tickers = corr_matrix.columns[order]
    reordered_corr = corr_matrix.loc[reordered_tickers, reordered_tickers]
    
    return reordered_corr, linkage_matrix


def calculate_rolling_correlation(
    prices: pd.DataFrame,
    asset1: str,
    asset2: str = "SPY",
    windows: List[int] = [20, 60]
) -> pd.DataFrame:
    """Calculates rolling Pearson correlation between two assets over given windows."""
    returns = np.log(prices / prices.shift(1)).dropna()
    df_roll = pd.DataFrame(index=returns.index)
    
    if asset1 in returns.columns and asset2 in returns.columns:
        s1 = returns[asset1]
        s2 = returns[asset2]
        for w in windows:
            df_roll[f"Corr {w}d"] = s1.rolling(window=w).corr(s2)
            
    return df_roll.dropna(how="all")


# -----------------------------------------------------------------------------
# Module 3: Concentration Risk Metrics (CR10 & HHI)
# -----------------------------------------------------------------------------
def calculate_cr10_and_hhi(holdings_list: List[Tuple[str, str, float]]) -> Dict:
    """Calculates CR10 and HHI."""
    weights = [w for _, _, w in holdings_list]
    cr10 = sum(weights)
    hhi = sum([(w)**2 for w in weights])
    
    if hhi < 1000:
        hhi_category = "Diversificado"
        hhi_badge = "success"
    elif hhi <= 1800:
        hhi_category = "Moderado"
        hhi_badge = "warning"
    else:
        hhi_category = "Altamente Concentrado"
        hhi_badge = "danger"
        
    return {
        "CR10": cr10,
        "HHI": hhi,
        "HHI_Category": hhi_category,
        "HHI_Badge": hhi_badge
    }


# -----------------------------------------------------------------------------
# Module 4: Technical Analysis & Indicators
# -----------------------------------------------------------------------------
def calculate_technical_indicators(prices_series: pd.Series) -> pd.DataFrame:
    """Calculates SMA50, SMA200, Bollinger Bands, Z-Score, and 20d/60d Realized Volatility."""
    df = pd.DataFrame({"Price": prices_series})
    
    df["SMA50"] = df["Price"].rolling(window=50).mean()
    df["SMA200"] = df["Price"].rolling(window=200).mean()
    df["SMA20"] = df["Price"].rolling(window=20).mean()
    
    roll_std_20 = df["Price"].rolling(window=20).std()
    df["Bollinger_Upper"] = df["SMA20"] + 2.0 * roll_std_20
    df["Bollinger_Lower"] = df["SMA20"] - 2.0 * roll_std_20
    
    roll_std_200 = df["Price"].rolling(window=200).std()
    df["Z_Score_200"] = (df["Price"] - df["SMA200"]) / roll_std_200
    
    daily_returns = np.log(df["Price"] / df["Price"].shift(1))
    df["Vol_20d_JGP"] = daily_returns.rolling(window=20).std() * config.VOL_ANNUALIZATION_FACTOR * 100.0
    df["Vol_60d_Trend"] = daily_returns.rolling(window=60).std() * config.VOL_ANNUALIZATION_FACTOR * 100.0
    
    return df


# -----------------------------------------------------------------------------
# Module 5: Sector Rotation & JGP Markowitz Optimization
# -----------------------------------------------------------------------------
def calculate_relative_strength(prices: pd.DataFrame, benchmark_ticker: str = "SPY") -> pd.DataFrame:
    """Calculates RS Ratio P_ETF / P_SPY."""
    if benchmark_ticker not in prices.columns:
        return pd.DataFrame()
    
    bm_series = prices[benchmark_ticker]
    rs_df = pd.DataFrame(index=prices.index)
    
    for col in prices.columns:
        rs_df[col] = prices[col] / bm_series
        
    return rs_df


def calculate_rrg_metrics(prices: pd.DataFrame, benchmark_ticker: str = "SPY", lookback: int = 14) -> pd.DataFrame:
    """Computes RRG 2D metrics: RS-Ratio and RS-Momentum."""
    rs_df = calculate_relative_strength(prices, benchmark_ticker)
    rrg_records = []
    
    for col in prices.columns:
        if col == benchmark_ticker:
            continue
        rs = rs_df[col].dropna()
        if len(rs) < lookback * 2:
            continue
            
        rs_sma = rs.rolling(window=lookback).mean()
        rs_ratio = 100.0 * (rs / rs_sma)
        rs_momentum = 100.0 * (rs_ratio / rs_ratio.shift(lookback))
        
        curr_ratio = rs_ratio.iloc[-1]
        curr_momo = rs_momentum.iloc[-1]
        
        if curr_ratio >= 100 and curr_momo >= 100:
            quadrant = "Leading"
        elif curr_ratio >= 100 and curr_momo < 100:
            quadrant = "Weakening"
        elif curr_ratio < 100 and curr_momo < 100:
            quadrant = "Lagging"
        else:
            quadrant = "Improving"
            
        rrg_records.append({
            "Ticker": col,
            "RS-Ratio": curr_ratio,
            "RS-Momentum": curr_momo,
            "Quadrant": quadrant
        })
        
    return pd.DataFrame(rrg_records)


def calculate_drawdowns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculates Underwater Drawdown series."""
    cummax = prices.cummax()
    return (prices - cummax) / cummax


def optimize_markowitz_jgp(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    target_returns: np.ndarray,
    max_capital_constraint: float = 1.0
) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray]]:
    """Generates Markowitz Efficient Frontier under JGP unleverage constraint sum(|w_i|) <= 1.0."""
    num_assets = len(expected_returns)
    frontier_vols = []
    frontier_rets = []
    weights_list = []
    
    init_weights = np.ones(num_assets) / num_assets
    bounds = tuple((0.0, max_capital_constraint) for _ in range(num_assets))
    
    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w: np.dot(w, expected_returns) - target}
        ]
        
        def obj_vol(w):
            return np.sqrt(np.dot(w.T, np.dot(cov_matrix.values, w))) * config.VOL_ANNUALIZATION_FACTOR
            
        res = minimize(obj_vol, init_weights, method="SLSQP", bounds=bounds, constraints=constraints)
        
        if res.success:
            frontier_vols.append(res.fun)
            frontier_rets.append(target)
            weights_list.append(res.x)
            
    return np.array(frontier_vols), np.array(frontier_rets), weights_list


# -----------------------------------------------------------------------------
# Module 6: Brazil Election Cycles Metrics
# -----------------------------------------------------------------------------
def calculate_political_risk_spread(prices_b3: pd.DataFrame) -> pd.Series:
    """Calculates Political Risk Spread: (PETR4 + BBAS3)/2 - (ITUB4 + BBDC4)/2."""
    returns = prices_b3.pct_change().fillna(0)
    
    estatais_cols = [c for c in ["PETR4", "BBAS3"] if c in returns.columns]
    privadas_cols = [c for c in ["ITUB4", "BBDC4"] if c in returns.columns]
    
    if estatais_cols and privadas_cols:
        r_estatais = returns[estatais_cols].mean(axis=1)
        r_privadas = returns[privadas_cols].mean(axis=1)
        spread = r_estatais - r_privadas
        return (1.0 + spread).cumprod() - 1.0
    return pd.Series(dtype=float)


def calculate_basket_performance(prices_b3: pd.DataFrame) -> pd.DataFrame:
    """Computes equal-weighted cumulative return curves for the 4 B3 sector baskets."""
    cum_returns = (prices_b3 / prices_b3.iloc[0]) * 100.0
    basket_df = pd.DataFrame(index=prices_b3.index)
    
    for basket_name, tickers in config.B3_SECTOR_BASKETS.items():
        clean_tickers = [t.replace(".SA", "") for t in tickers]
        avail = [t for t in clean_tickers if t in cum_returns.columns]
        if avail:
            basket_df[basket_name] = cum_returns[avail].mean(axis=1)
            
    return basket_df


def calculate_volatility_compression(
    prices_b3: pd.DataFrame,
    election_date: str = "2022-10-30"
) -> pd.DataFrame:
    """Calculates 20d volatility pre-1st round vs post-2nd round."""
    returns = np.log(prices_b3 / prices_b3.shift(1)).dropna()
    dt_election = pd.to_datetime(election_date)
    
    records = []
    for col in prices_b3.columns:
        series_ret = returns[col]
        pre_series = series_ret.loc[series_ret.index < dt_election].tail(20)
        post_series = series_ret.loc[series_ret.index >= dt_election].head(20)
        
        vol_pre = pre_series.std() * config.VOL_ANNUALIZATION_FACTOR * 100.0 if len(pre_series) > 5 else np.nan
        vol_post = post_series.std() * config.VOL_ANNUALIZATION_FACTOR * 100.0 if len(post_series) > 5 else np.nan
        
        delta_vol = vol_post - vol_pre if not (np.isnan(vol_pre) or np.isnan(vol_post)) else np.nan
        
        records.append({
            "Ticker": col,
            "Vol 20d Pre-Eleição (%)": vol_pre,
            "Vol 20d Pós-Eleição (%)": vol_post,
            "Compressão / Choque (pp)": delta_vol
        })
        
    return pd.DataFrame(records)
