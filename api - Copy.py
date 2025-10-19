# predictor.py
import pandas as pd
import numpy as np
from db import get_recent_ticks, add_log
from telegram_notifier import send_telegram
import datetime

def compute_indicators(df):
    df['ma9'] = df['close'].rolling(9).mean()
    df['ma21'] = df['close'].rolling(21).mean()
    df['rsi'] = compute_rsi(df['close'], 14)
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0).rolling(period).mean()
    down = -delta.clip(upper=0).rolling(period).mean()
    rs = up / (down + 1e-8)
    return 100 - (100 / (1 + rs))

def generate_signal(symbol):
    rows = get_recent_ticks(symbol, limit=200)
    if len(rows) < 30:
        return None

    df = pd.DataFrame(rows)[::-1]  # oldest -> newest
    df = compute_indicators(df)
    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal = None
    confidence = 0.0

    # Basic strategy
    if (prev['ma9'] < prev['ma21']) and (last['ma9'] > last['ma21']) and last['rsi'] < 70:
        signal = "BUY"
        confidence = min(0.95, 0.5 + (70 - last['rsi'])/100)
    elif (prev['ma9'] > prev['ma21']) and (last['ma9'] < last['ma21']) and last['rsi'] > 30:
        signal = "SELL"
        confidence = min(0.95, 0.5 + (last['rsi'] - 30)/100)
    else:
        signal = "HOLD"

    note = f"Signal {signal} for {symbol} | RSI: {round(float(last['rsi']),1)} | conf={round(float(confidence),2)}"
    add_log(note)

    # Optional: Telegram notification for strong signals
    if signal in ["BUY", "SELL"]:
        send_telegram(f"📈 {signal} {symbol}\nConfidence: {round(confidence,2)}\nRSI: {round(float(last['rsi']),1)}")

    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": round(float(confidence), 2),
        "reason": f"MA crossover + RSI {round(float(last['rsi']),1)}",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
