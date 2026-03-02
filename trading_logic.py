"""
trading_logic.py
Crypto Intelligence Pro — Market Data, Technical Indicators & Signal Engine
Supports offline/demo mode when internet is unavailable.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


COINS = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "BNB (BNB)": "BNB-USD",
    "XRP (XRP)": "XRP-USD",
}

PERIODS = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
}

# ── Demo seed prices (realistic starting points) ──────────────────────────────
_DEMO_SEED = {
    "BTC-USD": 87000.0,
    "ETH-USD": 3400.0,
    "SOL-USD": 175.0,
    "BNB-USD": 580.0,
    "XRP-USD": 0.62,
}

_PERIOD_DAYS = {
    "1mo": 30,
    "3mo": 90,
    "6mo": 180,
    "1y": 365,
}


def _is_online() -> bool:
    """Quick connectivity check."""
    try:
        import urllib.request
        urllib.request.urlopen("https://finance.yahoo.com", timeout=3)
        return True
    except Exception:
        return False


def _generate_demo_data(ticker: str, period: str) -> pd.DataFrame:
    """
    Generate realistic-looking synthetic OHLCV price data
    for offline / demo mode using a seeded random walk.
    """
    seed_price = _DEMO_SEED.get(ticker, 1000.0)
    days = _PERIOD_DAYS.get(period, 90)

    np.random.seed(42)
    returns = np.random.normal(0.001, 0.025, days)  # slight upward drift
    closes = [seed_price]
    for r in returns:
        closes.append(closes[-1] * (1 + r))
    closes = np.array(closes[1:])

    highs  = closes * (1 + np.abs(np.random.normal(0, 0.012, days)))
    lows   = closes * (1 - np.abs(np.random.normal(0, 0.012, days)))
    opens  = np.roll(closes, 1)
    opens[0] = closes[0] * 0.998
    volumes = np.random.uniform(1e9, 5e10, days)

    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=days, freq="D")

    df = pd.DataFrame({
        "Open":   opens,
        "High":   highs,
        "Low":    lows,
        "Close":  closes,
        "Volume": volumes,
    }, index=dates)

    return df


def fetch_price_data(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """
    Download OHLCV data from Yahoo Finance.
    Falls back to synthetic demo data if offline.
    """
    if _is_online():
        try:
            df = yf.download(ticker, period=period, interval="1d",
                             progress=False, auto_adjust=True)
            if not df.empty:
                df.dropna(inplace=True)
                return df
        except Exception as e:
            print(f"[trading_logic] Error fetching {ticker}: {e}")

    # ── Offline fallback ──────────────────────────────────────────────────────
    print(f"[trading_logic] Offline mode — using demo data for {ticker}.")
    return _generate_demo_data(ticker, period)


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index calculation."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_ma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window).mean()


def get_volatility(df: pd.DataFrame) -> dict:
    """Calculate daily return volatility and annualised volatility."""
    if df.empty or "Close" not in df.columns:
        return {"daily_vol": 0.0, "annual_vol": 0.0, "level": "Unknown"}

    close = df["Close"].squeeze()
    daily_returns = close.pct_change().dropna()
    daily_vol = float(daily_returns.std() * 100)
    annual_vol = float(daily_vol * np.sqrt(252))

    if annual_vol < 40:
        level = "LOW"
    elif annual_vol < 80:
        level = "MODERATE"
    else:
        level = "HIGH"

    return {"daily_vol": round(daily_vol, 2), "annual_vol": round(annual_vol, 2), "level": level}


def generate_signal(df: pd.DataFrame) -> dict:
    """
    Generate a BUY / SELL / HOLD signal from RSI + MA crossover logic.
    Returns a dict with signal, rsi_value, ma50, ma200, price, reasoning.
    """
    if df.empty or len(df) < 20:
        return {
            "signal": "HOLD",
            "rsi": None,
            "ma50": None,
            "ma200": None,
            "price": None,
            "reasoning": "Insufficient data.",
        }

    close = df["Close"].squeeze()

    rsi = calculate_rsi(close)
    ma50 = calculate_ma(close, 50)
    ma200 = calculate_ma(close, 200)

    latest_rsi   = float(rsi.iloc[-1]) if not rsi.empty else 50.0
    latest_ma50  = float(ma50.iloc[-1]) if not ma50.dropna().empty else None
    latest_ma200 = float(ma200.iloc[-1]) if not ma200.dropna().empty else None
    latest_price = float(close.iloc[-1])

    reasons = []
    buy_score = 0
    sell_score = 0

    # RSI signals
    if latest_rsi < 30:
        buy_score += 2
        reasons.append(f"RSI {latest_rsi:.1f} — Oversold (strong BUY pressure)")
    elif latest_rsi < 45:
        buy_score += 1
        reasons.append(f"RSI {latest_rsi:.1f} — Approaching oversold zone")
    elif latest_rsi > 70:
        sell_score += 2
        reasons.append(f"RSI {latest_rsi:.1f} — Overbought (strong SELL pressure)")
    elif latest_rsi > 60:
        sell_score += 1
        reasons.append(f"RSI {latest_rsi:.1f} — Approaching overbought zone")
    else:
        reasons.append(f"RSI {latest_rsi:.1f} — Neutral zone")

    # MA signals
    if latest_ma50 is not None:
        if latest_price > latest_ma50:
            buy_score += 1
            reasons.append(f"Price above 50-MA (${latest_ma50:,.2f}) — Bullish trend")
        else:
            sell_score += 1
            reasons.append(f"Price below 50-MA (${latest_ma50:,.2f}) — Bearish trend")

    if latest_ma200 is not None:
        if latest_price > latest_ma200:
            buy_score += 1
            reasons.append(f"Price above 200-MA (${latest_ma200:,.2f}) — Long-term bullish")
        else:
            sell_score += 1
            reasons.append(f"Price below 200-MA (${latest_ma200:,.2f}) — Long-term bearish")

    # Determine final signal
    if buy_score > sell_score and buy_score >= 2:
        signal = "BUY"
    elif sell_score > buy_score and sell_score >= 2:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "rsi": round(latest_rsi, 2),
        "ma50": round(latest_ma50, 2) if latest_ma50 else None,
        "ma200": round(latest_ma200, 2) if latest_ma200 else None,
        "price": round(latest_price, 2),
        "reasoning": " | ".join(reasons),
    }


def get_stop_loss_guidance(signal_data: dict, volatility: dict) -> dict:
    """Generate stop-loss and take-profit guidance based on signal + volatility."""
    price = signal_data.get("price")
    signal = signal_data.get("signal", "HOLD")
    vol_level = volatility.get("level", "MODERATE")

    if not price:
        return {}

    buffer_map = {"LOW": 0.05, "MODERATE": 0.08, "HIGH": 0.12}
    buffer = buffer_map.get(vol_level, 0.08)

    if signal == "BUY":
        stop_loss     = round(price * (1 - buffer), 2)
        take_profit_1 = round(price * 1.10, 2)
        take_profit_2 = round(price * 1.20, 2)
    elif signal == "SELL":
        stop_loss     = round(price * (1 + buffer), 2)
        take_profit_1 = round(price * 0.90, 2)
        take_profit_2 = round(price * 0.80, 2)
    else:
        stop_loss     = round(price * (1 - buffer), 2)
        take_profit_1 = round(price * 1.08, 2)
        take_profit_2 = round(price * 1.15, 2)

    return {
        "stop_loss": stop_loss,
        "take_profit_1": take_profit_1,
        "take_profit_2": take_profit_2,
        "buffer_pct": f"{buffer * 100:.0f}%",
    }
