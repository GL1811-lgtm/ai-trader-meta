# self_rewriter.py
import os
from db import add_log

def improve_predictor():
    """AI reviews its predictor code and updates it if necessary"""
    predictor_path = "predictor.py"

    with open(predictor_path, "r", encoding="utf-8") as f:
        code = f.read()

    improvements = []

    # Example 1: Add MACD indicator if not present
    if "MACD" not in code:
        macd_snippet = """
def compute_macd(df):
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
    return df
"""
        code = code.replace("def compute_indicators", macd_snippet + "\ndef compute_indicators")
        improvements.append("Added MACD indicator support")

    # Example 2: Ensure RSI smoothing is handled
    if "1e-8" in code:
        code = code.replace("1e-8", "1e-6  # improved stability")
        improvements.append("Improved RSI stability")

    if improvements:
        with open(predictor_path, "w", encoding="utf-8") as f:
            f.write(code)
        for i in improvements:
            add_log(f"Self-updated predictor.py: {i}")
        print("✅ Code self-improvement done:", improvements)
    else:
        print("No updates required today.")

if __name__ == "__main__":
    improve_predictor()
