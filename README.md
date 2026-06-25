# Personal AI/Tech Evening Scanner (Educational)

**This is a completely separate personal learning project.**

It lives in its own GitHub repository and has **nothing to do** with the frozen forward paper test (`SEMIS_MOM_CONF_2026-06__SIM`) in the main `Alpaca-Trading` repo.

## Purpose (Learning + Profitability Habits)

- Practice building a small, focused, friction-first alert system for the US evening window (power hour / close / after-hours) — convenient if you trade from the UK on a 9-5 schedule.
- Learn clean modular code: notifier (Discord) + scanner (simple rules) + scheduled execution (GitHub Actions) + a nice UI (Next.js on Vercel).
- Reinforce good habits: timestamped rationales at decision time, "open the broker yourself", paper mode by default, local + remote logging for later review, **large universe (~150 tickers) for statistical power on BNF trades**.
- The "BNF" (basic naive filter) here is deliberately naive and overfit-prone so you can experience the full loop of idea → alert → manual review → journal outcome.

**Strong safety rules in this project:**
- `PAPER_MODE=true` by default everywhere.
- No order execution code. Alerts only say "Open Robinhood and review".
- All outputs are educational. The real evidence work happens on the frozen strategy in the other repo.

## Quick Start

### 1. Discord Webhook (the notification channel)
1. In Discord, go to a server → Channel settings → Integrations → Webhooks → New Webhook.
2. Name it "Evening Scanner", choose a channel.
3. Copy the Webhook URL.
4. In your GitHub repo (this one) → Settings → Secrets and variables → Actions → New repository secret:
   - Name: `DISCORD_WEBHOOK_URL`
   - Value: the full webhook URL

(You can also set `AI_TECH_UNIVERSE` as a repo variable if you want to change the list without code changes.)

### 2. Local run (optional)
```bash
cp .env.example .env.local
# edit .env.local with your webhook (or leave PAPER_MODE)

pip install -r requirements.txt   # or just the packages
python scripts/evening_scanner.py
```

### 3. Scheduled scans (the "agent loop")
The `.github/workflows/evening-ai-scan.yml` runs Mon-Fri at 22:00 UTC (≈ 6pm ET).

It:
- Broad BNF scan on large AI/tech pool (not just usual stocks) using efficient batch yf
- ONLY real notifications (if matches>0): lists exact stocks + reasons + "what to check" + plan details
- Friction: open Robinhood yourself for the listed ones
- Uploads logs as artifacts
- Optionally commits `signals.jsonl` back to the repo (so your Vercel UI can show history)

Trigger manually anytime from the Actions tab.

## Vercel Deployment (the "app")

This repo is set up as a Next.js project — perfect for Vercel.

1. Push this repo to GitHub (new repo recommended).
2. Go to [vercel.com](https://vercel.com) → New Project → Import Git Repository.
3. Select this repo.
4. Deploy (no build env vars needed for the basic UI).
5. (Optional) In Vercel project settings you can add environment variables, but the Discord secret lives in **GitHub** (for the Action).

The deployed app gives you:
- Nice explanation of the system
- "Simulate scan" button (client-side demo so you can see what an alert looks like without waiting for cron)
- Instructions for setup
- Link to your Discord channel for the real alerts

Later you can enhance the UI to fetch the latest `signals.jsonl` (raw GitHub URL) or move the log to Supabase / Vercel KV.

## Project Structure

```
personal-ai-evening-scanner/
├── app/                    # Next.js UI (Vercel)
│   └── page.tsx            # Main dashboard + simulator
├── scripts/
│   ├── notifier.py         # Discord rich embeds + local logging (modular)
│   └── evening_scanner.py  # Educational BNF filter on large ~150 ticker pool + liquidity pre-filter + chunked yf
├── .github/workflows/
│   └── evening-ai-scan.yml # Scheduled + manual runs (the agent loop)
├── .env.example
├── README.md
└── signals.jsonl           # Created at runtime (gitignored)
```

## Educational Comments in Code

Every important file has extensive comments explaining:
- Why friction ("open the app yourself") is a feature, not a bug.
- Data biases (single-source yfinance, look-ahead, selection).
- Why this must stay separate from any frozen test.
- How the pieces (notifier, scanner, scheduler, UI) are intentionally modular.

## Next Steps / Playbook Ideas

- Run for a few weeks. Every signal that fires → manually note in your journal what you actually did and what happened 1-2 days later.
- Track hit rate, average move after signal, how often you would have followed through.
- Only after you have real personal data consider making the filter stricter or adding news.
- Compare the *discipline* of this small loop vs the heavy harness in the main project.

## Relationship to Main Repo

See the main `Alpaca-Trading` repo's `AGENTS.md` and `paper_test_tracker/real_paper_execution_test_plan_20260607.md`.

This scanner is **post-graduation thinking material** or pure side learning. During the current Path A frozen test on Alpaca paper for the one pre-registered strategy, new scanners, new brokers (Robinhood), and new idea generation are intentionally turned off.

The compliant daily work lives in `bin/daily_real_paper_capture.sh` + the GitHub `daily_tick_runner.yml`.

## License / Use

Personal educational use only. Not financial advice. Past performance (or simulated alerts) is not indicative of future results. Most systematic retail strategies have no edge net of costs.

Enjoy the learning loop!
