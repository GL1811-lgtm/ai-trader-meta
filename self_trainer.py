# self_trainer.py
import datetime
import pandas as pd
from db import get_recent_ticks, add_log
from predictor import compute_indicators
import numpy as np

# Configurable learning parameters (the AI can adjust these)
THRESHOLDS = {
    "buy_rsi": 70,
    "sell_rsi": 30,
    "ma_gap": 0.02  # 2% gap between MA9 and MA21
}

def evaluate_past_performance(symbol):
    """Evaluate how accurate previous signals were"""
    rows = get_recent_ticks(symbol, limit=300)
    if len(rows) < 50:
        return None

    df = pd.DataFrame(rows)[::-1]
    df = compute_indicators(df)

    df["signal"] = np.where((df["ma9"] > df["ma21"]) & (df["rsi"] < THRESHOLDS["buy_rsi"]), "BUY",
                    np.where((df["ma9"] < df["ma21"]) & (df["rsi"] > THRESHOLDS["sell_rsi"]), "SELL", "HOLD"))

    # Check profit/loss for past trades
    results = []
    for i in range(len(df) - 10):
        if df.iloc[i]["signal"] in ["BUY", "SELL"]:
            entry = df.iloc[i]["close"]
            future = df.iloc[i+10]["close"]
            change = (future - entry) / entry
            if df.iloc[i]["signal"] == "SELL":
                change *= -1
            results.append(change)

    if not results:
        return None

    avg_gain = np.mean(results)
    success_rate = np.sum(np.array(results) > 0) / len(results)

    return {
        "symbol": symbol,
        "avg_gain": avg_gain,
        "success_rate": success_rate
    }

def self_retrain():
    """AI adjusts its own logic thresholds based on performance"""
    symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

    log_summary = []
    for s in symbols:
        perf = evaluate_past_performance(s)
        if not perf:
            continue

        # Adjust RSI thresholds based on success rate
        if perf["success_rate"] < 0.5:
            THRESHOLDS["buy_rsi"] -= 1
            THRESHOLDS["sell_rsi"] += 1
        else:
            THRESHOLDS["buy_rsi"] += 0.5
            THRESHOLDS["sell_rsi"] -= 0.5

        note = (
            f"[{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Retrained {s} | Success={round(perf['success_rate']*100,2)}% "
            f"| AvgGain={round(perf['avg_gain']*100,2)}% "
            f"| New Thresholds={THRESHOLDS}"
        )
        print(note)
        add_log(note)
        log_summary.append(note)

    return log_summary

if __name__ == "__main__":
    logs = self_retrain()
    print("\n✅ Self-learning completed. Updated model thresholds.")
    for line in logs:
        print(line)
