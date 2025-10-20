# self_trainer.py
import os
import time
import json
import sqlite3
import datetime
from pathlib import Path
from telegram import Bot

# CONFIG
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8278881368:AAG87xbqMs5VgN8NuOonoNwNzu3f0-w1xtE")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "1571872533"))
PROJECT_ROOT = Path(__file__).parent
LEARNING_LOG = PROJECT_ROOT / "learning_log.txt"
CURRENT_METRICS_FILE = PROJECT_ROOT / "current_metrics.json"
DB_FILE = PROJECT_ROOT / "market.db"
REPORT_HOUR = 18
REPORT_MINUTE = 30

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram(text):
    """Send message to Telegram (trim if too long)."""
    try:
        bot.send_message(chat_id=ADMIN_CHAT_ID, text=text[:4000])
        print("✅ Telegram report sent.")
    except Exception as e:
        print("Telegram send error:", e)

def load_current_metrics():
    if CURRENT_METRICS_FILE.exists():
        try:
            return json.loads(CURRENT_METRICS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def compute_metrics_from_db(db_path):
    """Compute accuracy and PnL from SQLite signals/results table."""
    if not Path(db_path).exists():
        return None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('signals','results')")
        tbl = cur.fetchone()
        if not tbl:
            conn.close()
            return None
        table = tbl[0]
        cur.execute(f"SELECT predicted, actual, pnl FROM {table} WHERE predicted IS NOT NULL AND actual IS NOT NULL")
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return None
        total = len(rows)
        correct = sum(1 for r in rows if str(r[0]).lower() == str(r[1]).lower())
        pnl_vals = [float(r[2]) for r in rows if r[2] is not None]
        accuracy = correct / total if total else 0
        avg_pnl = sum(pnl_vals) / len(pnl_vals) if pnl_vals else 0
        return {"accuracy": round(accuracy, 4), "avg_pnl": round(avg_pnl, 4), "samples": total}
    except Exception as e:
        print("DB metrics error:", e)
        return None

def summarize_recent_logs(lines=30):
    if not LEARNING_LOG.exists():
        return "No learning log found."
    try:
        data = LEARNING_LOG.read_text(encoding="utf-8").strip().splitlines()
        recent = "\n".join(data[-lines:])
        return recent if recent else "Learning log empty."
    except Exception as e:
        return f"Error reading log: {e}"

def build_report():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    header = f"📈 Daily Learning Report — {now.strftime('%Y-%m-%d %H:%M:%S IST')}\n\n"
    db_metrics = compute_metrics_from_db(DB_FILE)
    current = load_current_metrics()

    if db_metrics:
        metrics_text = (
            f"- Accuracy (DB): {db_metrics['accuracy']*100:.2f}% over {db_metrics['samples']} samples\n"
            f"- Avg PnL: {db_metrics['avg_pnl']}\n"
        )
    elif current.get("accuracy") is not None:
        metrics_text = f"- Current recorded accuracy: {float(current.get('accuracy'))*100:.2f}%\n"
    else:
        metrics_text = "- No accuracy data available.\n"

    recent = summarize_recent_logs(40)
    suggestions = "\nSuggestions: None automated today.\n"
    report = header + metrics_text + "\nRecent learning log entries:\n" + recent + "\n" + suggestions
    return report, (db_metrics or current)

def save_metrics(metrics):
    try:
        CURRENT_METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("Failed to save metrics:", e)

def seconds_until_next_run(hour=REPORT_HOUR, minute=REPORT_MINUTE):
    tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now = datetime.datetime.now(tz)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += datetime.timedelta(days=1)
    return (target - now).total_seconds()

def run_once_and_schedule():
    report, metrics = build_report()
    send_telegram(report)
    if metrics:
        save_metrics(metrics)
    while True:
        secs = seconds_until_next_run()
        print(f"Sleeping for {int(secs)} seconds until next daily report.")
        time.sleep(secs)
        report, metrics = build_report()
        send_telegram(report)
        if metrics:
            save_metrics(metrics)

if __name__ == "__main__":
    run_once_and_schedule()
