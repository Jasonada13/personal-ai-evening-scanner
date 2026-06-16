#!/usr/bin/env python3
"""
evening_scanner.py

Personal educational scanner for US AI/tech names in the evening window.

=== CRITICAL DISCLAIMER ===
This is a standalone personal learning / experimentation project in its own repo.
It is NOT part of the frozen forward paper test (SEMIS_MOM_CONF_2026-06__SIM) in the main Alpaca-Trading repo.
Do not use signals from here to influence or compare against the frozen strategy.
New ideas/variants during the embargo on the main project are forbidden per AGENTS.md.

Purpose of this file:
- Teach practical concepts: moving average deviation (mean reversion), relative strength vs benchmark (QQQ), volume confirmation.
- Demonstrate a "BNF-style" (basic naive filter) with clear, commented rules.
- Enforce paper mode + heavy friction ("you must open Robinhood yourself").
- Produce timestamped, rationaled signals that you can journal and review later.
- Focus on evening US session (power hour / close / after hours) — convenient for UK 9-5.

Safety:
- Always runs in PAPER_MODE by default.
- No order submission code exists here.
- Small universe only.
- Rate limiting via yfinance (be nice).

Run locally:
  python scripts/evening_scanner.py

Scheduled via GitHub Action (recommended).
"""

import os
import sys
from datetime import datetime, timezone
from typing import List, Dict, Optional

# Add parent so we can import notifier when run from anywhere
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))

try:
    from notifier import send_discord_signal
except Exception:
    # Fallback if run in weird context
    def send_discord_signal(ticker, reason, rationale, **kwargs):
        print(f"[FALLBACK] Would alert: {ticker} | {reason}")
        print(f"Rationale: {rationale}")

import yfinance as yf  # pip install yfinance

# Config via env (GitHub secrets or .env)
PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() in ("true", "1", "yes")
UNIVERSE = [x.strip().upper() for x in os.getenv(
    "AI_TECH_UNIVERSE", "NVDA,AMD,TSLA,PLTR,SMCI,AVGO"
).split(",") if x.strip()]

def compute_bnf_signal(ticker: str) -> Optional[Dict]:
    """
    Basic Naive Filter (BNF-style) — educational example only.

    Rules (transparent and overfit-prone on purpose for learning):
    1. Price is meaningfully below 20-day MA (oversold / mean-reversion setup).
    2. Today's volume is significantly above recent average (confirmation / interest).
    3. Ticker has shown positive relative strength vs QQQ over last ~20 days (participation in tech move).
    4. (Stub) Simple "news" filter — we don't actually scrape; you can extend later with RSS or manual.

    Returns a signal dict or None.
    All numbers and thresholds are illustrative — tune only after you have your own journaled outcomes.
    """
    try:
        # Fetch recent daily bars (60 days for decent MA + volume avg)
        hist = yf.download(
            ticker,
            period="60d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )
        if hist.empty or len(hist) < 25:
            return None

        price = float(hist["Close"].iloc[-1])
        ma20 = float(hist["Close"].tail(20).mean())
        dev_pct = (price - ma20) / ma20 * 100.0

        vol_today = float(hist["Volume"].iloc[-1])
        avg_vol = float(hist["Volume"].tail(20).mean() or 1)
        vol_mult = vol_today / avg_vol

        # Relative strength vs QQQ (approx 20-day)
        qqq = yf.download("QQQ", period="60d", progress=False, auto_adjust=True, threads=False)
        if not qqq.empty and len(qqq) >= 20:
            t_ret = (price / float(hist["Close"].iloc[-20]) - 1) * 100
            q_ret = (float(qqq["Close"].iloc[-1]) / float(qqq["Close"].iloc[-20]) - 1) * 100
            rs_vs_qqq = t_ret - q_ret
        else:
            rs_vs_qqq = 0.0

        # === The actual naive filter ===
        OVERSOLD_THRESHOLD = -5.0   # 5%+ below 20DMA
        VOL_SURGE = 1.4             # 40%+ above avg volume

        if dev_pct < OVERSOLD_THRESHOLD and vol_mult > VOL_SURGE and rs_vs_qqq > 0:
            reason = (
                f"Dev {dev_pct:.1f}% below 20DMA | "
                f"Vol {vol_mult:.1f}x avg | "
                f"RS vs QQQ +{rs_vs_qqq:.1f}%"
            )
            rationale = (
                "Educational BNF (basic naive filter) triggered in evening window. "
                "Price pulled back vs its short MA while volume picked up and the name held up better than the broader tech benchmark. "
                "This is a classic mean-reversion + momentum confluence pattern on high-beta AI/semiconductor-related names. "
                "Single-source daily data (yfinance). Strong look-ahead and selection bias. "
                "In the main frozen test project we are not allowed to generate or act on new variants during embargo. "
                "Use this only for personal learning and outcome journaling. Review what actually happened 24-48h later."
            )
            return {
                "ticker": ticker,
                "reason": reason,
                "rationale": rationale,
                "dev_pct": round(dev_pct, 2),
                "vol_mult": round(vol_mult, 2),
                "rs_vs_qqq": round(rs_vs_qqq, 2),
            }
    except Exception as e:
        print(f"[scanner] Error on {ticker}: {e}")
    return None

def run_evening_scan():
    print(f"\n[evening_scanner] Starting educational AI/tech evening scan — {datetime.now(timezone.utc).isoformat()}")
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


    # FORCED TEST ALERT - will be reverted immediately after this test run
    send_discord_signal(
        "FAKE99",
        "FAKE INDICATOR (forced via GitHub Action): Dev -8.5% below 20DMA | Vol 2.1x avg | RS vs QQQ +7.2%",
        "FORCED TEST RUN: This alert is being emitted from the GitHub Action (full pipeline: secret load -> Python execution -> notifier) to verify the Discord webhook integration is working end-to-end. No real market data or BNF scan performed. This is purely a controlled test of the Action + secret + webhook path. Educational only. Ignore this alert for any trading purposes."
    )

    if not signals_found:
        print("  No signals met the BNF criteria this run.")

    print("\n[evening_scanner] Scan complete. Check Discord for rich alerts (if any).")
    print("Remember: This is paper/educational. The real disciplined work is on the frozen strategy real paper fills.")
    return signals_found

if __name__ == "__main__":
    run_evening_scan()
