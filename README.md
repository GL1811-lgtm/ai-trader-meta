AI Options Alert - Starter (Windows)

Contents:
- fetcher.py           # fetches market data and stores in SQLite
- db.py                # simple SQLite helper
- predictor.py         # rule-based signals + learning log writer
- api.py               # FastAPI server to return alerts & logs
- telegram_notifier.py # sends Telegram alerts
- requirements.txt

How to run (Windows)
1. Open PowerShell in this folder.
2. Create venv:
   python -m venv venv
3. Activate:
   .\venv\Scripts\Activate.ps1
4. Install:
   pip install -r requirements.txt
5. Edit telegram_notifier.py and set TOKEN and CHAT_ID.
6. Start fetcher in one terminal:
   python fetcher.py
7. Start API server in another:
   python api.py

Notes:
- This is an MVP. Replace placeholder tokens before using.
- Use localhost for testing. For 24/7 run, deploy to cloud later.
