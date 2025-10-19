# telegram_notifier.py
import requests
import os

# Create a bot with @BotFather and put token & chat_id here or use environment variables
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8278881368:AAG87xbqMs5VgN8NuOonoNwNzu3f0-w1xtE')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '1571872533')


def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("telegram error", e)
