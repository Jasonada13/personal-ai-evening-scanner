#!/usr/bin/env python3
"""
Full Evening Reversion Scanner

Educational BNF-style scanner for US AI/tech names in the evening window.
Fixed for pandas compatibility.

This is the personal learning project — separate from the frozen test.
"""

import os
import sys
from datetime import datetime, timezone
from typing import List, Dict, Optional

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))

try:
    from notifier import send_discord_signal
except Exception:
    def send_discord_signal(ticker, reason, rationale, **kwargs):
        print(f"[FALLBACK] Would alert: {ticker} | {reason}")
        print(f"Rationale: {rationale}")

import yfinance as yf

PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() in ("true", "1", "yes")
UNIVERSE = [x.strip().upper() for x in os.getenv(
    "AI_TECH_UNIVERSE", "NVDA,AMD,TSLA,PLTR,SMCI,AVGO"
).split(",") if x.strip()]

def compute_bnf_signal(ticker: str) -> Optional[Dict]:
    """
    Basic Naive Filter (BNF-style) — educational example only.

    Rules:
    1. Price meaningfully below 20-day MA.
    2. Volume significantly above average.
    3. Positive relative strength vs QQQ.
    """
    try:
        hist = yf.download(
            ticker,
            period="60d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )
        if hist.empty or len(hist) < 25:
            return None

        # Fixed pandas access
        close = hist["Close"]
        price = float(close.iloc[-1].item())
        ma20 = float(close.tail(20).mean().item())
        dev_pct = (price - ma20) / ma20 * 100.0

        vol_today = float(hist["Volume"].iloc[-1].item())
        avg_vol = float(hist["Volume"].tail(20).mean().item() or 1)
        vol_mult = vol_today / avg_vol

        qqq = yf.download("QQQ", period="60d", progress=False, auto_adjust=True, threads=False)
        if not qqq.empty and len(qqq) >= 20:
            q_close = qqq["Close"]
            t_ret = (price / float(close.iloc[-20].item()) - 1) * 100
            q_ret = (float(q_close.iloc[-1].item()) / float(q_close.iloc[-20].item()) - 1) * 100
            rs_vs_qqq = t_ret - q_ret
        else:
            rs_vs_qqq = 0.0

        OVERSOLD_THRESHOLD = -5.0
        VOL_SURGE = 1.4

        if dev_pct < OVERSOLD_THRESHOLD and vol_mult > VOL_SURGE and rs_vs_qqq > 0:
            reason = (
                f"Dev {dev_pct:.1f}% below 20DMA | "
                f"Vol {vol_mult:.1f}x avg | "
                f"RS vs QQQ +{rs_vs_qqq:.1f}%"
            )
            rationale = (
                "Educational BNF triggered in evening window. "
                "Price pulled back vs short MA with volume and relative strength. "
                "Single-source yfinance data with known delays and biases. "
                "Dedicated Plan: 1. Open Robinhood and search the ticker. "
                "2. Review chart, volume, news against your rules. "
                "3. Journal the signal with this rationale. "
                "4. Track outcome in 24-48h and log in your dedicated plan tracker. "
                "This is for consistent evening practice only. "
                "Aligns with your single dedicated plan for disciplined review and journaling. "
                "In-sample only — not for the main frozen test."
            )
            return {
                "ticker": ticker,
                "reason": reason,
                "rationale": rationale,
            }
    except Exception as e:
        print(f"[scanner] Error on {ticker}: {e}")
    return None

def run_evening_scan():
    print(f"\n[evening_scanner] Starting Full Evening Reversion Scanner — {datetime.now(timezone.utc).isoformat()}")
    print(f"Universe: {UNIVERSE}")
    print(f"PAPER_MODE={PAPER_MODE}\n")

    signals_found = []

    for ticker in UNIVERSE:
        sig = compute_bnf_signal(ticker)
        if sig:
            signals_found.append(sig)
            send_discord_signal(
                sig["ticker"],
                sig["reason"],
                sig["rationale"],
            )
            print(f"  ✓ Signal generated for {ticker}")

    # Always send a dedicated plan test alert for the evening window to ensure full alert is delivered
    # (educational, labeled as such)
    send_discord_signal(
        "EVENING",
        "Full alert test for dedicated plan: Evening Reversion practice window active",
        "This is the full alert with Robinhood instruction. "
        "Dedicated Plan Details: Follow your single dedicated plan every evening — "
        "scan for reversion setups on AI/tech names, open Robinhood to review the specific ticker, "
        "apply your personal risk rules and journal template, record the outcome the next day. "
        "Use this for consistent practice. Paper/educational only. "
        "No auto orders. Friction-first: you must manually review and decide."
    )
    print("  ✓ Full dedicated plan alert sent for evening review practice")

    if not signals_found:
        print("  No real BNF signals met criteria this run (expected — data dependent).")
    print("\n[evening_scanner] Scan complete. Check Discord for the full alert with plan details.")
    return signals_found

if __name__ == "__main__":
    run_evening_scan()
