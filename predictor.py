# predictor.py
import pandas as pd
import numpy as np
from db import get_recent_ticks, add_log
from telegram_notifier import send_telegram
import datetime

# --- Technical Indicator Calculations ---

def compute_rsi(series, period=14):
    """Compute the RSI (Relative Strength Index)"""
    delta = series.diff()
    up = delta.clip(lower=0).rolling(period).mean()
    down = -delta.clip(upper=0).rolling(period).mean()
    rs = up / (down + 1e-6  # improved stability)
    return 100 - (100 / (1 + rs))


def compute_macd(df):
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
    return df

def compute_indicators(df):
    """Compute Moving Averages and RSI indicators"""
    df['ma9'] = df['close'].rolling(9).mean()
    df['ma21'] = df['close'].rolling(21).mean()
    df['rsi'] = compute_rsi(df['close'], 14)
    return df

# --- Signal Generation Logic ---

def generate_signal(symbol):
    """Generate buy/sell signals using indicators"""
    rows = get_recent_ticks(symbol, limit=200)
    if len(rows) < 30:
        return None

    df = pd.DataFrame(rows)[::-1]  # oldest -> newest
    df = compute_indicators(df)
    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal = None
    confidence = 0.0

    if (prev['ma9'] < prev['ma21']) and (last['ma9'] > last['ma21']) and last['rsi'] < 70:
        signal = "BUY"
        confidence = min(0.95, 0.5 + (70 - last['rsi'])/100)
    elif (prev['ma9'] > prev['ma21']) and (last['ma9'] < last['ma21']) and last['rsi'] > 30:
        signal = "SELL"
        confidence = min(0.95, 0.5 + (last['rsi'] - 30)/100)

    if signal:
        note = f"Signal {signal} for {symbol} conf={confidence} reason=MA crossover + RSI {round(float(last['rsi']),1)}"
        add_log(note)

    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": round(float(confidence),2),
        "reason": f"MA crossover + RSI {round(float(last['rsi']),1)}",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

def daily_learning_summary():
    """Placeholder for daily learning summary"""
    note = "Daily retrain: updated thresholds based on last 50 trades (placeholder)"
    add_log(note)

if __name__ == "__main__":
    for s in ["^NSEI","RELIANCE.NS"]:
        sig = generate_signal(s)
        if sig and sig['signal']:
            send_telegram(f"{sig['signal']} {sig['symbol']} | conf:{sig['confidence']} | {sig['reason']}")
