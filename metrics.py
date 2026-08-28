"""
metrics.py - Quantitative Calculation Engine & Mathematical Functions for JGP 2026 Dashboard
"""

import numpy as np
import pandas as pd
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
from scipy.optimize import minimize
from typing import Tuple, Dict, List, Optional
import config


# -----------------------------------------------------------------------------
# Module 1: Tactical Returns & Q4 Seasonality
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


def calculate_q4_seasonality(
    prices: pd.DataFrame,
    start_year: int = 2022,
    end_year: int = 2025
) -> pd.DataFrame:
    """
    Calculates historical Q4 (16 weeks / ~80 trading days) returns for the past 4 years
    and computes Win Rate (% of years exceeding JGP Hurdle Rate +1.56%).
    """
    records = []
    
    for ticker in prices.columns:
        series = prices[ticker].dropna()
        yearly_q4_returns = []
        
        for year in range(start_year, end_year + 1):
            q4_start = f"{year}-08-28"
            q4_end = f"{year}-12-18"
            
            sub = series.loc[(series.index >= q4_start) & (series.index <= q4_end)]
            if len(sub) > 5:
                q4_ret = (sub.iloc[-1] / sub.iloc[0]) - 1.0
                yearly_q4_returns.append(q4_ret)
        
        if yearly_q4_returns:
            mean_ret = np.mean(yearly_q4_returns)
            median_ret = np.median(yearly_q4_returns)
            win_rate = np.mean([r >= config.HURDLE_RATE_PRO_RATA for r in yearly_q4_returns]) * 100.0
            
            rec = {
                "Ticker": ticker,
                "Mean Q4 Return": mean_ret,
                "Median Q4 Return": median_ret,
                "Win Rate (%)": win_rate
            }
            for i, year in enumerate(range(start_year, end_year + 1)):
                if i < len(yearly_q4_returns):
                    rec[f"Q4 {year}"] = yearly_q4_returns[i]
                else:
                    rec[f"Q4 {year}"] = np.nan
            records.append(rec)
            
    df_res = pd.DataFrame(records)
    if not df_res.empty:
        df_res = df_res.sort_values(by="Mean Q4 Return", ascending=False).reset_index(drop=True)
    return df_res


# -----------------------------------------------------------------------------
# Module 2: Correlation Matrix & Ward Linkage Hierarchical Clustering
# -----------------------------------------------------------------------------
def calculate_correlation_matrix(prices: pd.DataFrame, window: Optional[int] = None) -> pd.DataFrame:
    """Calculates Pearson correlation matrix on daily log returns for lookback window."""
    log_ret = np.log(prices / prices.shift(1)).dropna()
    if window and len(log_ret) > window:
        log_ret = log_ret.tail(window)
    return log_ret.corr(method="pearson")


def perform_ward_clustering(corr_matrix: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Performs Ward's linkage hierarchical clustering on correlation matrix using
    Euclidean distance d_ij = sqrt(2 * (1 - rho_ij)).
    Returns reordered correlation matrix and linkage matrix.
    """
    # Clip correlations to [-1, 1] to prevent floating point instability
    corr_clipped = np.clip(corr_matrix.values, -1.0, 1.0)
    dist_matrix = np.sqrt(2.0 * (1.0 - corr_clipped))
    
    # Convert square distance matrix to condensed form for scipy.cluster.hierarchy
    condensed_dist = squareform(dist_matrix, checks=False)
    linkage_matrix = hierarchy.linkage(condensed_dist, method="ward")
    
    # Reorder matrix based on dendrogram leaves
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
    """
    Calculates CR10 (sum of top 10 holdings weights) and HHI (Herfindahl-Hirschman Index).
    HHI = sum((w_i * 100)^2)
    """
    weights = [w for _, _, w in holdings_list]
    cr10 = sum(weights)
    hhi = sum([(w)**2 for w in weights])  # w is already in percentage (e.g. 7.15 for 7.15%)
    
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
# Module 4: Technical Analysis & JGP 20d Volatility Regime
# -----------------------------------------------------------------------------
def calculate_technical_indicators(prices_series: pd.Series) -> pd.DataFrame:
    """
    Calculates SMA50, SMA200, Bollinger Bands (20d, 2std), Z-Score, and 20d/60d Realized Volatility.
    """
    df = pd.DataFrame({"Price": prices_series})
    
    # Simple Moving Averages
    df["SMA50"] = df["Price"].rolling(window=50).mean()
    df["SMA200"] = df["Price"].rolling(window=200).mean()
    df["SMA20"] = df["Price"].rolling(window=20).mean()
    
    # Bollinger Bands (20d, 2std)
    roll_std_20 = df["Price"].rolling(window=20).std()
    df["Bollinger_Upper"] = df["SMA20"] + 2.0 * roll_std_20
    df["Bollinger_Lower"] = df["SMA20"] - 2.0 * roll_std_20
    
    # Z-Score relative to SMA200
    roll_std_200 = df["Price"].rolling(window=200).std()
    df["Z_Score_200"] = (df["Price"] - df["SMA200"]) / roll_std_200
    
    # Realized Volatility Annualized (20d JGP official vs 60d trend)
    daily_returns = np.log(df["Price"] / df["Price"].shift(1))
    df["Vol_20d_JGP"] = daily_returns.rolling(window=20).std() * config.VOL_ANNUALIZATION_FACTOR * 100.0
    df["Vol_60d_Trend"] = daily_returns.rolling(window=60).std() * config.VOL_ANNUALIZATION_FACTOR * 100.0
    
    return df


# -----------------------------------------------------------------------------
# Module 5: Sector Rotation, Drawdown & JGP Markowitz Efficient Frontier
# -----------------------------------------------------------------------------
def calculate_relative_strength(
    prices: pd.DataFrame,
    benchmark_ticker: str = "SPY"
) -> pd.DataFrame:
    """Calculates Relative Strength Ratio RS = P_ETF / P_SPY."""
    if benchmark_ticker not in prices.columns:
        return pd.DataFrame()
    
    bm_series = prices[benchmark_ticker]
    rs_df = pd.DataFrame(index=prices.index)
    
    for col in prices.columns:
        rs_df[col] = prices[col] / bm_series
        
    return rs_df


def calculate_rrg_metrics(prices: pd.DataFrame, benchmark_ticker: str = "SPY", lookback: int = 14) -> pd.DataFrame:
    """
    Computes 2D Relative Rotation Graph (RRG) metrics:
    - RS-Ratio (trend component)
    - RS-Momentum (rate of change of RS-Ratio)
    Categorizes into 4 Quadrants: Leading, Weakening, Lagging, Improving.
    """
    rs_df = calculate_relative_strength(prices, benchmark_ticker)
    rrg_records = []
    
    for col in prices.columns:
        if col == benchmark_ticker:
            continue
        rs = rs_df[col].dropna()
        if len(rs) < lookback * 2:
            continue
            
        # RS-Ratio: normalized ratio centered around 100
        rs_sma = rs.rolling(window=lookback).mean()
        rs_ratio = 100.0 * (rs / rs_sma)
        
        # RS-Momentum: rate of change of RS-Ratio centered around 100
        rs_momentum = 100.0 * (rs_ratio / rs_ratio.shift(lookback))
        
        curr_ratio = rs_ratio.iloc[-1]
        curr_momo = rs_momentum.iloc[-1]
        
        # Determine RRG Quadrant
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
    """
    Calculates Underwater Drawdown series DD_t = (P_t - max(P_s)) / max(P_s).
    """
    cummax = prices.cummax()
    drawdown = (prices - cummax) / cummax
    return drawdown


def optimize_markowitz_jgp(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    target_returns: np.ndarray,
    max_capital_constraint: float = 1.0
) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray]]:
    """
    Generates Markowitz Efficient Frontier under strict JGP Unleverage constraint sum(|w_i|) <= 1.0.
    
    min w^T Sigma w
    s.t. w^T mu = target_return
         sum(|w_i|) <= 1.0
    """
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
# Module 6: Brazil Election Cycles (2010, 2014, 2018, 2022) Metrics
# -----------------------------------------------------------------------------
def calculate_political_risk_spread(prices_b3: pd.DataFrame) -> pd.Series:
    """
    Calculates Political Risk Spread:
    Delta_pol,t = (R_PETR4 + R_BBAS3)/2 - (R_ITUB4 + R_BBDC4)/2
    """
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
    """
    Computes equal-weighted cumulative return curves for the 4 B3 sector baskets.
    """
    cum_returns = (prices_b3 / prices_b3.iloc[0]) * 100.0  # Base 100
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
    """
    Calculates 20d volatility pre-1st round vs post-2nd round and the volatility compression delta:
    Delta_vol = Vol_20d(Post) - Vol_20d(Pre)
    """
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
