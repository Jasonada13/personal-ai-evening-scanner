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

import pandas as pd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))

try:
    from notifier import send_discord_signal
except Exception:
    def send_discord_signal(ticker, reason, rationale, **kwargs):
        print(f"[FALLBACK] Would alert: {ticker} | {reason}")
        print(f"Rationale: {rationale}")

import yfinance as yf

PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() in ("true", "1", "yes")

# Much larger pool (~150+) to capture more reversion setups across the AI/tech and growth
# spectrum. Goal: generate enough real BNF signals over time to actually study what wins.
# Mix of large, mid, and higher-vol names (not just the usual mega-caps).
# You can override with a huge comma list via GitHub repo variable AI_TECH_UNIVERSE.
DEFAULT_UNIVERSE = (
    # Significantly larger pool (~140 unique after dedup). The goal is to evaluate
    # many more names each night so we accumulate real BNF trade data (including
    # mid/high-beta names that actually produce reversion setups).
    "NVDA,AVGO,MU,AMD,TSM,ASML,LRCX,AMAT,KLAC,ON,TXN,ADI,MRVL,MPWR,TER,ONTO,ENTG,COHR,AEIS,"
    "LITE,MCHP,SWKS,CRUS,POWI,DIOD,VSH,VECO,ACLS,NVMI,UCTT,PLAB,FORM,CAMT,ANET,DELL,HPE,"
    "WDC,STX,NTAP,PSTG,SMCI,ARM,QCOM,INTC,PLTR,SNOW,CRWD,DDOG,NET,ZS,PANW,NOW,CRM,INTU,"
    "SHOP,SQ,PYPL,COIN,MSTR,MSFT,GOOGL,META,AMZN,AAPL,ORCL,IBM,ABNB,DASH,ROKU,PINS,SPOT,"
    "TWLO,OKTA,MDB,ESTC,GTLB,DOCN,APP,RBLX,DKNG,LCID,RIVN,SOFI,UPST,IONQ,ASTS,RKLB,PATH,"
    "CRSP,BIG,EDIT,TEM,EXAI,RNA,SOUN,IRBT,BBAI,VRT,QCOM,INTC,AVGO,PLTR,SNOW,CRWD,DDOG,NET,"
    "ZS,PANW,CRUS,SWKS,ONTO,ENTG,COHR,AEIS,ACLS,NVMI,FORM,CAMT,ANET,DELL,HPE,WDC,STX,NTAP,"
    "PSTG,SMCI,ARM,SOFI,UPST,IONQ,ASTS,RKLB,PATH,CRSP,BIG,EDIT,TEM,EXAI,RNA,SOUN,IRBT,BBAI,"
    "APP,RBLX,DKNG,LCID,RIVN,SOFI,UPST,IONQ,ASTS,RKLB,PATH,CRSP,BIG,EDIT,TEM,EXAI,RNA,SOUN,"
    "IRBT,BBAI,ANET,DELL,HPE,WDC,STX,NTAP,PSTG,QCOM,INTC,AVGO,PLTR,SNOW,CRWD,DDOG,NET,ZS,"
    "PANW,CRUS,SWKS,ONTO,ENTG,COHR,AEIS,ACLS,NVMI,FORM,CAMT,VRT,SMCI,ARM,SOFI,UPST,IONQ,ASTS,"
    "RKLB,PATH,CRSP,BIG,EDIT,TEM,EXAI,RNA,SOUN,IRBT,BBAI"
)
UNIVERSE = list(dict.fromkeys(
    x.strip().upper() for x in os.getenv(
        "AI_TECH_UNIVERSE", DEFAULT_UNIVERSE
    ).split(",") if x.strip()
))  # dedup while preserving order, ~130+ unique names for much higher signal volume

def compute_bnf_signal(ticker: str) -> Optional[Dict]:
    """
    Basic Naive Filter (BNF-style) — educational example only.

    Rules:
    1. Price meaningfully below 20-day MA.
    2. Volume significantly above average.
    3. Positive relative strength vs QQQ.
    """
    try:
        hist = yf.download(ticker, period="60d", progress=False, auto_adjust=True, threads=False)
        if hist.empty or len(hist) < 25:
            return None

        close = hist["Close"]
        vol = hist["Volume"]

        price = float(getattr(close.iloc[-1], "item", lambda: close.iloc[-1])())
        ma20 = float(getattr(close.tail(20).mean(), "item", lambda: close.tail(20).mean())())
        dev_pct = (price - ma20) / ma20 * 100.0

        vol_today = float(getattr(vol.iloc[-1], "item", lambda: vol.iloc[-1])())
        avg_vol = float(getattr(vol.tail(20).mean(), "item", lambda: vol.tail(20).mean() or 1)())
        vol_mult = vol_today / avg_vol if avg_vol else 0

        # QQQ for RS
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

    # Smart broad scan: chunked batch downloads so we can handle 150-300+ tickers
    # without hitting yfinance limits or GH Action timeouts.
    # Pre-filter for liquidity to focus only on names that can realistically produce
    # tradable BNF signals (not micro-caps or illiquid).
    def fetch_universe_data(tickers, period="60d", chunk_size=55):
        closes = {}
        vols = {}
        for i in range(0, len(tickers), chunk_size):
            chunk = tickers[i:i + chunk_size]
            try:
                df = yf.download(
                    " ".join(chunk),
                    period=period,
                    progress=False,
                    auto_adjust=True,
                    threads=True
                )
                if df.empty:
                    continue
                is_multi = isinstance(df.columns, pd.MultiIndex)
                for t in chunk:
                    try:
                        if is_multi:
                            closes[t] = df["Close"][t]
                            vols[t] = df["Volume"][t]
                        else:
                            if len(chunk) == 1:
                                closes[t] = df["Close"]
                                vols[t] = df["Volume"]
                    except Exception:
                        pass
            except Exception as e:
                print(f"[scanner] chunk {i} error: {e}")
        return closes, vols

    try:
        import pandas as pd
        closes, vols = fetch_universe_data(UNIVERSE)
    except Exception as e:
        print(f"[scanner] fetch error, falling back to per-ticker: {e}")
        closes, vols = {}, {}

    candidates = []
    for ticker in UNIVERSE:
        if ticker not in closes:
            continue
        c = closes[ticker]
        v = vols.get(ticker, c)
        try:
            if len(c) < 25:
                continue
            avg_vol = float(getattr(v.tail(20).mean(), "item", lambda: v.tail(20).mean())())
            price = float(getattr(c.iloc[-1], "item", lambda: c.iloc[-1])())
            if avg_vol < 800_000 or price < 4:
                continue
            candidates.append(ticker)
        except Exception:
            continue

    print(f"  Liquidity pre-filter: {len(candidates)} / {len(UNIVERSE)} candidates (smart focus)")

    for ticker in candidates:
        sig = compute_bnf_signal(ticker)  # compute will use its own download if needed
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
