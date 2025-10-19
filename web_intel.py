# web_intel.py
import requests
import time
import datetime
from db import add_log

SYMBOLS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "^NSEI", "^NSEBANK"]

def fetch_news(symbol="RELIANCE.NS"):
    """Fetch latest financial news headlines from Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={symbol}"
        res = requests.get(url, timeout=10).json()
        headlines = []
        for item in res.get("news", []):
            headlines.append(item.get("title", ""))
        add_log(f"Fetched {len(headlines)} news for {symbol}")
        return headlines
    except Exception as e:
        add_log(f"Error fetching news for {symbol}: {e}")
        return []

def analyze_sentiment(headlines):
    """Simple sentiment analyzer using keyword matching"""
    positive_words = ["gain", "growth", "surge", "profit", "bullish", "up"]
    negative_words = ["loss", "fall", "drop", "bearish", "down", "crash"]

    sentiment_score = 0
    for h in headlines:
        title = h.lower()
        if any(p in title for p in positive_words):
            sentiment_score += 1
        if any(n in title for n in negative_words):
            sentiment_score -= 1

    sentiment = "neutral"
    if sentiment_score > 2:
        sentiment = "positive"
    elif sentiment_score < -2:
        sentiment = "negative"

    add_log(f"Sentiment: {sentiment} ({sentiment_score})")
    return sentiment

def continuous_learning():
    """Run 24/7, fetching and analyzing data every few minutes"""
    while True:
        print(f"[{datetime.datetime.now()}] 🌐 Gathering market intelligence...")
        for symbol in SYMBOLS:
            headlines = fetch_news(symbol)
            if headlines:
                sentiment = analyze_sentiment(headlines)
                print(f"📰 {symbol}: {sentiment}")
        add_log("Completed one web intelligence cycle.")
        time.sleep(600)  # wait 10 minutes before next run

if __name__ == "__main__":
    continuous_learning()
