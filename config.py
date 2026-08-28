"""
config.py - Expanded Configuration parameters and constants for JGP 2026 Quantitative Dashboard
"""

import numpy as np

# -----------------------------------------------------------------------------
# JGP 2026 Rules & Competition Parameters
# -----------------------------------------------------------------------------
TRADING_DAYS_PER_YEAR = 252
TACTICAL_WEEKS = 16
TACTICAL_TRADING_DAYS = 80  # ~80 business days

# Hurdle rate: 5.0% per annum (Fed Funds rate for unallocated cash)
HURDLE_RATE_ANNUAL = 0.05
# Pro-rata hurdle rate for 16 weeks / 80 trading days: (1 + 0.05)^(80/252) - 1 ≈ 1.56%
HURDLE_RATE_PRO_RATA = (1.0 + HURDLE_RATE_ANNUAL) ** (TACTICAL_TRADING_DAYS / TRADING_DAYS_PER_YEAR) - 1.0

# Short position borrowing cost: 0.4% per month (~1/20 per day = 0.0002 daily)
SHORT_BORROWING_COST_MONTHLY = 0.004
SHORT_BORROWING_COST_DAILY = SHORT_BORROWING_COST_MONTHLY / 20.0

# Volatility annualization factor and default rolling windows
VOL_ANNUALIZATION_FACTOR = np.sqrt(TRADING_DAYS_PER_YEAR)
VOL_WINDOW_JGP = 20  # Official JGP 20-day window
VOL_WINDOW_TREND = 60  # Trend comparison window

# Short-term metrics windows (in trading days)
SHORT_TERM_1M_DAYS = 21  # 1 Month (~21 trading days)
SHORT_TERM_3M_DAYS = 63  # 3 Months (~63 trading days)

# Macro Base Windows (1 to 3 Years)
MACRO_WINDOWS = {
    "1 Ano (252d)": 252,
    "2 Anos (504d)": 504,
    "3 Anos (756d)": 756
}

# -----------------------------------------------------------------------------
# Eligible Universe (18 ETFs) & Sector Classifications
# -----------------------------------------------------------------------------
BENCHMARK_TICKER = "SPY"

ETF_CATEGORIES = {
    "Benchmark / Core": ["SPY"],
    "US Sectors": ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY", "XTN"],
    "International": ["EWJ", "EWG", "EEM", "EWZ"],
    "Macro / Safe-Havens": ["TLT", "GLD", "FXE"]
}

SECTOR_TYPES = {
    "Cíclicos / Crescimento": ["XLK", "XLY", "XLI", "XLB"],
    "Defensivos": ["XLU", "XLP", "XLV"],
    "Financeiro & Energia": ["XLF", "XLE"],
    "Outros / Macro": ["XTN", "EWJ", "EWG", "EEM", "EWZ", "TLT", "GLD", "FXE", "SPY"]
}

ALL_ETFS = [
    "SPY", "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY", "XTN",
    "EWJ", "EWG", "EEM", "EWZ", "TLT", "GLD", "FXE"
]

ETF_NAMES = {
    "SPY": "S&P 500 ETF Trust",
    "XLB": "Materials Select Sector SPDR",
    "XLE": "Energy Select Sector SPDR",
    "XLF": "Financial Select Sector SPDR",
    "XLI": "Industrial Select Sector SPDR",
    "XLK": "Technology Select Sector SPDR",
    "XLP": "Consumer Staples Select Sector SPDR",
    "XLU": "Utilities Select Sector SPDR",
    "XLV": "Health Care Select Sector SPDR",
    "XLY": "Consumer Discretionary Select SPDR",
    "XTN": "SPDR S&P Transportation ETF",
    "EWJ": "iShares MSCI Japan ETF",
    "EWG": "iShares MSCI Germany ETF",
    "EEM": "iShares MSCI Emerging Markets ETF",
    "EWZ": "iShares MSCI Brazil ETF",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "GLD": "SPDR Gold Shares",
    "FXE": "Invesco CurrencyShares Euro Trust"
}

# -----------------------------------------------------------------------------
# B3 Top Holdings Universe (Module 6 - Brazil Elections)
# -----------------------------------------------------------------------------
B3_SECTOR_BASKETS = {
    "Estatais": ["PETR4.SA", "BBAS3.SA", "ELET3.SA"],
    "Financeiro Privado": ["ITUB4.SA", "BBDC4.SA", "B3SA3.SA"],
    "Commodities / Exportadoras": ["VALE3.SA", "PRIO3.SA", "SUZB3.SA"],
    "Consumo Doméstico / Indústria": ["WEGE3.SA", "ABEV3.SA", "RENT3.SA"]
}

ALL_B3_TICKERS = [
    "PETR4.SA", "BBAS3.SA", "ELET3.SA",
    "ITUB4.SA", "BBDC4.SA", "B3SA3.SA",
    "VALE3.SA", "PRIO3.SA", "SUZB3.SA",
    "WEGE3.SA", "ABEV3.SA", "RENT3.SA"
]

B3_TICKER_NAMES = {
    "PETR4.SA": "Petrobras PN",
    "BBAS3.SA": "Banco do Brasil ON",
    "ELET3.SA": "Eletrobras ON",
    "ITUB4.SA": "Itaú Unibanco PN",
    "BBDC4.SA": "Bradesco PN",
    "B3SA3.SA": "B3 ON",
    "VALE3.SA": "Vale ON",
    "PRIO3.SA": "PRIO ON",
    "SUZB3.SA": "Suzano ON",
    "WEGE3.SA": "WEG ON",
    "ABEV3.SA": "Ambev ON",
    "RENT3.SA": "Localiza ON"
}

ELECTION_YEARS = [2010, 2014, 2018, 2022]

# -----------------------------------------------------------------------------
# ETF Top 10 Holdings Composition Data (Module 3)
# -----------------------------------------------------------------------------
ETF_TOP10_HOLDINGS = {
    "SPY": [
        ("MSFT", "Microsoft Corp", 7.15),
        ("AAPL", "Apple Inc", 6.85),
        ("NVDA", "NVIDIA Corp", 6.30),
        ("AMZN", "Amazon.com Inc", 3.75),
        ("META", "Meta Platforms Inc", 2.45),
        ("GOOGL", "Alphabet Inc Class A", 2.05),
        ("BRK.B", "Berkshire Hathaway", 1.75),
        ("GOOG", "Alphabet Inc Class C", 1.70),
        ("AVGO", "Broadcom Inc", 1.65),
        ("ELI", "Eli Lilly & Co", 1.50)
    ],
    "XLK": [
        ("MSFT", "Microsoft Corp", 22.40),
        ("AAPL", "Apple Inc", 21.80),
        ("NVDA", "NVIDIA Corp", 19.50),
        ("AVGO", "Broadcom Inc", 4.80),
        ("ORCL", "Oracle Corp", 2.60),
        ("CSCO", "Cisco Systems Inc", 2.10),
        ("ACN", "Accenture Plc", 1.90),
        ("ADBE", "Adobe Inc", 1.85),
        ("CRM", "Salesforce Inc", 1.80),
        ("AMD", "Advanced Micro Devices", 1.75)
    ],
    "XLF": [
        ("BRK.B", "Berkshire Hathaway", 13.20),
        ("JPM", "JPMorgan Chase & Co", 9.80),
        ("V", "Visa Inc", 7.90),
        ("MA", "Mastercard Inc", 6.50),
        ("BAC", "Bank of America Corp", 4.30),
        ("WFC", "Wells Fargo & Co", 3.70),
        ("GS", "Goldman Sachs Group", 3.10),
        ("MS", "Morgan Stanley", 2.60),
        ("SPGI", "S&P Global Inc", 2.40),
        ("AXP", "American Express Co", 2.20)
    ],
    "XLE": [
        ("XOM", "Exxon Mobil Corp", 23.10),
        ("CVX", "Chevron Corp", 15.40),
        ("COP", "ConocoPhillips", 8.20),
        ("EOG", "EOG Resources Inc", 4.90),
        ("SLB", "Schlumberger Ltd", 4.30),
        ("MPC", "Marathon Petroleum", 4.10),
        ("PSX", "Phillips 66", 3.80),
        ("VLO", "Valero Energy Corp", 3.50),
        ("WMB", "Williams Cos Inc", 3.20),
        ("OKE", "ONEOK Corp", 2.90)
    ],
    "EWZ": [
        ("VALE3", "Vale SA", 14.80),
        ("PETR4", "Petrobras PN", 11.20),
        ("ITUB4", "Itaú Unibanco PN", 8.90),
        ("PETR3", "Petrobras ON", 7.10),
        ("BBDC4", "Bradesco PN", 4.50),
        ("BBAS3", "Banco do Brasil ON", 3.80),
        ("WEGE3", "WEG SA", 3.20),
        ("B3SA3", "B3 SA", 3.10),
        ("ABEV3", "Ambev SA", 2.70),
        ("RENT3", "Localiza Rent a Car", 2.40)
    ],
    "TLT": [
        ("US20Y", "US Treasury Bond 20Y", 12.50),
        ("US22Y", "US Treasury Bond 22Y", 11.80),
        ("US25Y", "US Treasury Bond 25Y", 10.40),
        ("US27Y", "US Treasury Bond 27Y", 9.90),
        ("US30Y", "US Treasury Bond 30Y", 9.20),
        ("US19Y", "US Treasury Bond 19Y", 8.70),
        ("US21Y", "US Treasury Bond 21Y", 8.10),
        ("US24Y", "US Treasury Bond 24Y", 7.50),
        ("US26Y", "US Treasury Bond 26Y", 6.90),
        ("US28Y", "US Treasury Bond 28Y", 5.80)
    ],
    "GLD": [
        ("GOLD_BARS", "Physical Gold Bullion (100%)", 100.0)
    ],
    "FXE": [
        ("EUR_CASH", "Euro Currency Deposits (100%)", 100.0)
    ]
}

DEFAULT_GENERIC_HOLDINGS = [
    ("TOP1", "Primary Holdings Concentration", 8.5),
    ("TOP2", "Secondary Holdings Concentration", 6.8),
    ("TOP3", "Tertiary Asset Allocation", 5.9),
    ("TOP4", "Core Equity Constituent A", 4.7),
    ("TOP5", "Core Equity Constituent B", 4.2),
    ("TOP6", "Core Equity Constituent C", 3.8),
    ("TOP7", "Mid-Weight Holdings X", 3.3),
    ("TOP8", "Mid-Weight Holdings Y", 2.9),
    ("TOP9", "Diversified Basket Asset 1", 2.4),
    ("TOP10", "Diversified Basket Asset 2", 2.1)
]
