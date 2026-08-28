"""
test_engine.py - Smoke test script to verify data loading and quantitative metrics engine
"""

import config
import data_loader
import metrics
import pandas as pd
import numpy as np

print("--- Step 1: Testing Data Loader ---")
prices = data_loader.fetch_etf_data(config.ALL_ETFS, start_date="2024-01-01")
print(f"Downloaded prices shape: {prices.shape}")
print(f"Tickers retrieved: {list(prices.columns)}")

print("\n--- Step 2: Testing Module 1 (Cumulative Returns & Q4 Seasonality) ---")
cum_ret = metrics.calculate_cumulative_returns(prices)
print(f"Cumulative returns shape: {cum_ret.shape}")
short_ret = metrics.calculate_short_returns(prices)
print(f"Short returns shape: {short_ret.shape}")
seas_df = metrics.calculate_q4_seasonality(prices)
print(f"Seasonality summary top 3:\n{seas_df.head(3)}")

print("\n--- Step 3: Testing Module 2 (Correlation & Ward Clustering) ---")
corr = metrics.calculate_correlation_matrix(prices, window=20)
print(f"Correlation matrix shape: {corr.shape}")
reordered_corr, linkage = metrics.perform_ward_clustering(corr)
print(f"Reordered correlation matrix shape: {reordered_corr.shape}")

print("\n--- Step 4: Testing Module 3 (CR10 & HHI) ---")
holdings = config.ETF_TOP10_HOLDINGS.get("EWZ")
res_hhi = metrics.calculate_cr10_and_hhi(holdings)
print(f"EWZ CR10: {res_hhi['CR10']:.2f}%, HHI: {res_hhi['HHI']:.0f}, Category: {res_hhi['HHI_Category']}")

print("\n--- Step 5: Testing Module 4 (Technical Indicators) ---")
tech = metrics.calculate_technical_indicators(prices["SPY"])
print(f"SPY technical indicators tail:\n{tech.tail(2)}")

print("\n--- Step 6: Testing Module 5 (Relative Strength, RRG & Markowitz Frontier) ---")
rs = metrics.calculate_relative_strength(prices)
rrg = metrics.calculate_rrg_metrics(prices)
print(f"RRG metrics count: {len(rrg)}")

exp_returns = prices.pct_change().dropna().mean() * 252
cov_matrix = prices.pct_change().dropna().cov()
targets = np.linspace(exp_returns.min(), exp_returns.max(), 10)
f_vols, f_rets, weights = metrics.optimize_markowitz_jgp(exp_returns, cov_matrix, targets)
print(f"Markowitz frontier points computed: {len(f_vols)}")

print("\n--- Step 7: Testing Module 6 (B3 Election Cycles Data) ---")
b3_prices = data_loader.fetch_election_year_data(config.ALL_B3_TICKERS, 2022)
print(f"B3 election 2022 prices shape: {b3_prices.shape}")
pol_spread = metrics.calculate_political_risk_spread(b3_prices)
print(f"Political spread calculated, latest value: {pol_spread.iloc[-1]:.4f}")

print("\nSUCCESS: All quantitative engine functions executed cleanly without error!")
