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
# Broad curated pool for max qualifying coverage (AI/tech with volatility for reversion, 
# not just usual megacaps). Override via GH var or edit. ~40-50 to keep GH Action fast.
# Includes Semis + software/AI + high-beta/emerging (inspired by main project layer lists).
UNIVERSE = [x.strip().upper() for x in os.getenv(
    "AI_TECH_UNIVERSE", 
    "NVDA,AVGO,MU,AMD,TSM,ASML,LRCX,AMAT,KLAC,PLTR,SNOW,CRWD,DDOG,NET,ZS,ARM,SOUN,UPST,IONQ,ASTS,RKLB,PATH,CRSP,MSFT,GOOGL,META,AMZN,AAPL,ORCL,IBM,PANW,NOW,CRM,INTU,SHOP,SQ,PYPL,COIN,MSTR,SMCI"
).split(",") if x.strip()]

def compute_bnf_signal(ticker: str, hist_multi=None) -> Optional[Dict]:
    """
    Basic Naive Filter (BNF-style) — educational example only.

    Rules:
    1. Price meaningfully below 20-day MA.
    2. Volume significantly above average.
    3. Positive relative strength vs QQQ.
    """
    try:
        if hist_multi is not None and ticker in getattr(hist_multi.get("Close"), "columns", []):
            close = hist_multi["Close"][ticker]
            vol = hist_multi["Volume"][ticker]
        else:
            hist = yf.download(ticker, period="60d", progress=False, auto_adjust=True, threads=False)
            if hist.empty or len(hist) < 25:
                return None
            close = hist["Close"]
            vol = hist["Volume"]

        if len(close) < 25:
            return None

        price = float(getattr(close.iloc[-1], "item", lambda: close.iloc[-1])())
        ma20 = float(getattr(close.tail(20).mean(), "item", lambda: close.tail(20).mean())())
        dev_pct = (price - ma20) / ma20 * 100.0

        vol_today = float(getattr(vol.iloc[-1], "item", lambda: vol.iloc[-1])())
        avg_vol = float(getattr(vol.tail(20).mean(), "item", lambda: vol.tail(20).mean() or 1)())
        vol_mult = vol_today / avg_vol if avg_vol else 0

        # QQQ still per for simplicity (small)
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
                "Broad pool used to find non-usual stocks meeting criteria. In-sample only."
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
    print(f"Universe size: {len(UNIVERSE)} (broad pool for non-usual coverage)")
    print(f"PAPER_MODE={PAPER_MODE}\n")

    signals_found = []

    # Efficient batch download (yfinance supports multi for speed on larger pools)
    try:
        multi = " ".join(UNIVERSE)
        hist_multi = yf.download(multi, period="60d", progress=False, auto_adjust=True, threads=True)
    except Exception as e:
        print(f"[scanner] batch download error: {e}")
        hist_multi = None

    for ticker in UNIVERSE:
        sig = compute_bnf_signal(ticker, hist_multi=hist_multi)  # pass for potential reuse
        if sig:
            signals_found.append(sig)
            print(f"  ✓ Signal generated for {ticker}")

    # ONLY real notifications: send if matches (batched for list of stocks)
    if signals_found:
        try:
            send_discord_signals(signals_found)
        except NameError:
            # fallback if not updated notifier yet
            for s in signals_found:
                send_discord_signal(s["ticker"], s["reason"], s["rationale"])
        print(f"  ✓ Full alert sent for {len(signals_found)} stocks + dedicated plan details")
    else:
        print("  No real BNF signals met criteria this run — no notification sent (only real checks).")

    print("\n[evening_scanner] Scan complete. Only real criteria matches trigger Discord (with exact stocks + what to check).")
    return signals_found

if __name__ == "__main__":
    run_evening_scan()
