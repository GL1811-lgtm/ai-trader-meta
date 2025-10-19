import os
import time
import datetime
import logging
from telegram import Bot

# Basic config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

def send_message(text):
    try:
        bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=text)
    except Exception as e:
        print("Telegram send error:", e)

def main():
    send_message("✅ Meta Controller Online\nStatus: Active on Render Cloud")
    print("Meta controller started.")

    while True:
        # Example loop
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Running heartbeat check...")
        time.sleep(60)  # run every 60 seconds

if __name__ == "__main__":
    main()
