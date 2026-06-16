#!/usr/bin/env python3
"""
notifier.py

Standalone Discord rich notification sender for personal evening scanner.

=== IMPORTANT: This is a SEPARATE personal learning project ===
Do NOT merge or copy this logic into the main Alpaca-Trading / frozen test repo.
This exists only for educational exploration of alerts, friction, and journaling.

Features:
- Rich Discord embeds with ticker, reason, action ("Check on Robinhood"), rationale, timestamp.
- Friction-first design: never auto-trades. Always tells human to open app and review.
- Paper mode: safe by default.
- Local signal logging to signals.jsonl for your own review/journal.

Usage (local):
  python scripts/notifier.py --ticker NVDA --reason "..." --rationale "..."

In GitHub Action: the webhook comes from secrets.DISCORD_WEBHOOK_URL
"""

import os
import json
import argparse
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict

load_dotenv = None
try:
    from dotenv import load_dotenv
except ImportError:
    pass

if load_dotenv:
    load_dotenv()

WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL", "")
PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() in ("true", "1", "yes")

PROJECT_ROOT = Path(__file__).parent.parent
SIGNALS_LOG = PROJECT_ROOT / "signals.jsonl"

def log_signal_locally(ticker: str, reason: str, rationale: str, extra: Optional[Dict] = None):
    """Append to local JSONL for personal journaling and the Vercel dashboard."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "ticker": ticker.upper(),
        "reason": reason,
        "rationale": rationale,
        "paper": PAPER_MODE,
        "source": "evening-ai-scanner",
    }
    if extra:
        entry.update(extra)
    try:
        with open(SIGNALS_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[notifier] Logged locally to {SIGNALS_LOG}")
    except Exception as e:
        print(f"[notifier] Local log failed: {e}")

def send_discord_signal(
    ticker: str,
    reason: str,
    rationale: str,
    action_text: Optional[str] = None,
) -> bool:
    """Send rich embed to Discord. Returns success."""
    if not action_text:
        action_text = f"Open the Robinhood app (or robinhood.com/stocks/{ticker}) → search {ticker} → review the chart, volume, and any news yourself. This is an educational alert only."

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    embed = {
        "title": "📈 US AI/Tech Evening Window — Personal Alert",
        "description": f"**Check {ticker} on Robinhood**",
        "color": 0x3b82f6,  # nice blue
        "fields": [
            {"name": "Filter / Reason", "value": reason, "inline": False},
            {"name": "Rationale (at signal time)", "value": rationale[:1000], "inline": False},
            {"name": "Recommended Action", "value": action_text, "inline": False},
            {"name": "Generated", "value": timestamp, "inline": True},
            {"name": "Mode", "value": "PAPER / EDUCATIONAL • No auto orders • 1% risk discipline recommended", "inline": True},
        ],
        "footer": {
            "text": "Personal learning scanner • Friction > automation • Review outcome tomorrow"
        },
    }

    payload = {
        "embeds": [embed],
        "username": "Evening Scanner",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/5968/5968885.png",  # optional
    }

    if PAPER_MODE or not WEBHOOK:
        print("[notifier] PAPER MODE or no webhook — would have sent:")
        print(json.dumps(embed, indent=2))
        log_signal_locally(ticker, reason, rationale)
        return True

    try:
        resp = requests.post(WEBHOOK, json=payload, timeout=20)
        resp.raise_for_status()
        log_signal_locally(ticker, reason, rationale)
        print(f"[notifier] Discord alert sent for {ticker}")
        return True
    except Exception as e:
        print(f"[notifier] Discord send failed: {e}")
        log_signal_locally(ticker, reason, rationale)  # still log locally
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--rationale", required=True)
    args = parser.parse_args()

    send_discord_signal(args.ticker, args.reason, args.rationale)
