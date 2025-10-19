import yfinance as yf
import datetime, time
from db import insert_tick

# Example symbols
SYMBOLS = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

def fetch_once():
    for s in SYMBOLS:
        try:
            print(f"Fetching data for {s}...")
            t = yf.Ticker(s)
            # Fetch last 1 day of 5-minute data
            hist = t.history(period="1d", interval="5m")
            if hist.empty:
                print(f"No data for {s}")
                continue

            for idx, row in hist.tail(5).iterrows():  # insert last few rows
                data = {
                    "symbol": s,
                    "timestamp": idx.to_pydatetime(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row.get("Volume", 0) or 0)
                }
                insert_tick(data)
                print(f"Inserted {s} at {idx}")

        except Exception as e:
            print("fetch error", s, e)

if __name__ == "__main__":
    fetch_once()
    print("✅ Done inserting sample data.")
