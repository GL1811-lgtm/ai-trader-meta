# meta_controller.py  – simulation / learning only
import os
import time
import json
import shutil
import datetime
from pathlib import Path
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CallbackQueryHandler
from sandbox_runner import run_sandbox

# --- CONFIG ---
TELEGRAM_TOKEN = "8278881368:AAH52TzSQVudnEaz_2CiH_Tyu4frtTL_jWw"
ADMIN_CHAT_ID = "1571872533"          # your chat ID
AUTO_PROMOTE_MIN_GAIN = 0.02
CHECK_INTERVAL_SECONDS = 10           # fast loop (simulation only)

PROJECT_ROOT = Path(__file__).parent
DRAFT_PATH = PROJECT_ROOT / "predictor_draft.py"
PROD_PATH = PROJECT_ROOT / "predictor.py"
CODE_VERSIONS_DIR = PROJECT_ROOT / "code_versions"
CURRENT_METRICS_FILE = PROJECT_ROOT / "current_metrics.json"
LEARNING_LOG = PROJECT_ROOT / "learning_log.txt"

bot = Bot(token=TELEGRAM_TOKEN)
PENDING = {}

# -------------------------------------------------
def add_log(msg):
    ts = datetime.datetime.now().isoformat()
    print(f"[{ts}] {msg}")
    with open(LEARNING_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def load_current_accuracy():
    if CURRENT_METRICS_FILE.exists():
        try:
            return float(json.loads(CURRENT_METRICS_FILE.read_text()).get("accuracy", 0.0))
        except Exception:
            pass
    return 0.0

def save_current_metrics(metrics):
    CURRENT_METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

def promote_draft(draft_path: Path):
    CODE_VERSIONS_DIR.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if PROD_PATH.exists():
        backup = CODE_VERSIONS_DIR / f"predictor_backup_{ts}.py"
        shutil.copy2(PROD_PATH, backup)
        add_log(f"Backed up predictor -> {backup.name}")
    new_ver = CODE_VERSIONS_DIR / f"predictor_v{ts}.py"
    shutil.copy2(draft_path, new_ver)
    shutil.copy2(draft_path, PROD_PATH)
    add_log(f"Promoted draft -> {new_ver.name}")

# -------------------------------------------------
def send_approval_request(summary, draft_snippet, metrics):
    req_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    text = (
        f"⚠️ Meta AI Proposed Change (id={req_id})\n\n"
        f"{summary}\n\nSandbox metrics:\n{json.dumps(metrics)}\n\n"
        f"Snippet:\n{draft_snippet[:800]}"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Approve", callback_data=f"approve::{req_id}"),
         InlineKeyboardButton("❌ Reject", callback_data=f"reject::{req_id}")],
        [InlineKeyboardButton("📄 View Details", callback_data=f"view::{req_id}")],
        [InlineKeyboardButton("✅ Accept All", callback_data="approve_all")]
    ]
    PENDING[req_id] = {"metrics": metrics, "draft_path": str(DRAFT_PATH)}
    bot.send_message(int(ADMIN_CHAT_ID), text=text,
                     reply_markup=InlineKeyboardMarkup(keyboard))
    add_log(f"Sent approval id={req_id}")

def handle_callback(update: Update, context):
    query = update.callback_query
    data = query.data
    if data == "approve_all":
        for rid, meta in list(PENDING.items()):
            try:
                promote_draft(Path(meta["draft_path"]))
                save_current_metrics(meta["metrics"])
                add_log(f"Accept-All promoted id={rid}")
            except Exception as e:
                add_log(f"Error Accept-All id={rid}: {e}")
        PENDING.clear()
        query.edit_message_text("✅ All drafts approved.")
        return

    try:
        action, rid = data.split("::", 1)
    except ValueError:
        query.edit_message_text("Bad callback data.")
        return
    meta = PENDING.get(rid)
    if not meta:
        query.edit_message_text("Request expired.")
        return

    if action == "approve":
        promote_draft(Path(meta["draft_path"]))
        save_current_metrics(meta["metrics"])
        query.edit_message_text(f"✅ Approved id={rid}")
        add_log(f"Approved id={rid}")
        PENDING.pop(rid, None)
    elif action == "reject":
        query.edit_message_text(f"❌ Rejected id={rid}")
        add_log(f"Rejected id={rid}")
        PENDING.pop(rid, None)
    elif action == "view":
        preview = Path(meta["draft_path"]).read_text()[:4000]
        bot.send_message(int(ADMIN_CHAT_ID),
                         text=f"Full Draft (truncated):\n\n{preview}")
        query.edit_message_text(f"Sent preview id={rid}")

def start_telegram_bot():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CallbackQueryHandler(handle_callback))
    updater.start_polling(drop_pending_updates=True)
    add_log("Telegram listener started.")
    return updater

# -------------------------------------------------
def orchestrator_loop():
    add_log("Meta orchestrator loop starting.")
    while True:
        try:
            if DRAFT_PATH.exists():
                add_log("Detected predictor_draft.py – running sandbox.")
                metrics = run_sandbox(str(DRAFT_PATH))
                current_acc = load_current_accuracy()
                draft_acc = current_acc + float(metrics.get("accuracy_gain", 0.0))
                gain = draft_acc - current_acc
                add_log(f"Current={current_acc:.4f} | Draft={draft_acc:.4f} | Gain={gain:.4f}")
                snippet = DRAFT_PATH.read_text()[:1000]

                if gain >= AUTO_PROMOTE_MIN_GAIN:
                    promote_draft(DRAFT_PATH)
                    save_current_metrics({"accuracy": draft_acc})
                    try:
                        DRAFT_PATH.unlink(missing_ok=True)
                    except Exception:
                        pass
                    percent = round(draft_acc * 100, 2)
                    bot.send_message(
                        int(ADMIN_CHAT_ID),
                        text=f"✅ Draft auto-promoted (gain={gain:.4f}) | Current Accuracy: {percent}%"
                    )
                else:
                    send_approval_request("Auto-suggested improvement", snippet,
                                          {"accuracy": draft_acc, **metrics})
            time.sleep(CHECK_INTERVAL_SECONDS)
        except Exception as e:
            add_log(f"Loop error: {e}")
            time.sleep(10)

# -------------------------------------------------
if __name__ == "__main__":
    CODE_VERSIONS_DIR.mkdir(exist_ok=True)
    updater = start_telegram_bot()
    bot.send_message(int(ADMIN_CHAT_ID),
                     text="✅ Meta Controller Online (Testing Mode) — Watching for drafts.")
    orchestrator_loop()
