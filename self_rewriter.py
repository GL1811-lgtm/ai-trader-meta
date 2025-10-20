import os
import re
import time
import json
import datetime
import random
from pathlib import Path

# Self Rewriter
# This file creates a new predictor_draft.py with small, safe improvements
# which the Meta Controller will later test and possibly promote

PROJECT_ROOT = Path(__file__).parent
PREDICTOR_PATH = PROJECT_ROOT / "predictor.py"
DRAFT_PATH = PROJECT_ROOT / "predictor_draft.py"
CHANGE_LOG = PROJECT_ROOT / "rewriter_log.txt"


def log_change(msg: str):
    ts = datetime.datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(CHANGE_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_predictor_code() -> str:
    """Reads the current predictor.py safely"""
    try:
        return PREDICTOR_PATH.read_text(encoding="utf-8")
    except Exception as e:
        log_change(f"Error reading predictor.py: {e}")
        return ""


def modify_parameters(code: str) -> str:
    """Looks for numeric constants like RSI or MA thresholds and modifies them slightly"""
    # Example simple tweaks
    pattern_rsi = re.compile(r"rsi_threshold\s*=\s*(\d+)")
    pattern_ma = re.compile(r"moving_average\s*=\s*(\d+)")
    new_code = code

    # random safe adjustments
    rsi_delta = random.choice([-5, -3, -2, 2, 3, 5])
    ma_delta = random.choice([-10, -5, 5, 10])

    # apply regex-based replacements
    if pattern_rsi.search(new_code):
        new_code = pattern_rsi.sub(lambda m: f"rsi_threshold = {max(10, int(m.group(1)) + rsi_delta)}", new_code)
        log_change(f"Adjusted RSI threshold by {rsi_delta}")
    if pattern_ma.search(new_code):
        new_code = pattern_ma.sub(lambda m: f"moving_average = {max(5, int(m.group(1)) + ma_delta)}", new_code)
        log_change(f"Adjusted Moving Average window by {ma_delta}")

    return new_code


def add_learning_comment(code: str) -> str:
    """Add a learning signature comment at the top"""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"# Auto-generated draft by self_rewriter on {ts}\n"
    return header + code


def write_draft(new_code: str):
    """Write the modified code to predictor_draft.py"""
    try:
        DRAFT_PATH.write_text(new_code, encoding="utf-8")
        log_change(f"✅ New draft created: {DRAFT_PATH.name}")
    except Exception as e:
        log_change(f"❌ Error writing draft: {e}")


def rewriter_loop():
    """Main loop that periodically creates new predictor drafts"""
    log_change("Self Rewriter started. Watching predictor.py for improvements...")
    last_run = None

    while True:
        try:
            # run every 5 minutes or when predictor.py changes
            mtime = PREDICTOR_PATH.stat().st_mtime
            if last_run is None or time.time() - last_run > 300 or random.random() < 0.2:
                code = read_predictor_code()
                if code:
                    new_code = modify_parameters(code)
                    draft = add_learning_comment(new_code)
                    write_draft(draft)
                last_run = time.time()
            time.sleep(60)
        except KeyboardInterrupt:
            log_change("Stopped manually.")
            break
        except Exception as e:
            log_change(f"Error in rewriter loop: {e}")
            time.sleep(30)


if __name__ == "__main__":
    rewriter_loop()
