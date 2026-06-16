'use client';

import React, { useState } from 'react';

interface SimulatedSignal {
  ticker: string;
  reason: string;
  rationale: string;
  timestamp: string;
}

export default function PersonalEveningScanner() {
  const [signals, setSignals] = useState<SimulatedSignal[]>([]);
  const [isScanning, setIsScanning] = useState(false);

  // Educational BNF-style simulation (client side, no real data fetch)
  // This mirrors the spirit of the Python scanner for demo purposes in the Vercel UI.
  const runSimulatedScan = () => {
    setIsScanning(true);

    // Simulate a short delay like a real scan would take
    setTimeout(() => {
      const demoSignals: SimulatedSignal[] = [
        {
          ticker: "NVDA",
          reason: "Dev -6.8% below 20DMA | Vol 1.9x avg | RS vs QQQ +4.2%",
          rationale: "Educational demo of the BNF filter: price pulled back vs short MA on elevated volume while holding relative strength in the tech complex. Single-source daily bars. Strong selection and look-ahead bias. Use only for learning the full alert → manual review → journal loop. In the real frozen test project we do not generate or act on new variants during embargo.",
          timestamp: new Date().toISOString(),
        },
      ];

      setSignals(prev => [...demoSignals, ...prev].slice(0, 5)); // keep last 5
      setIsScanning(false);
    }, 850);
  };

  const exampleAction = (ticker: string) =>
    `Open the Robinhood app or go to robinhood.com/stocks/${ticker} → search for ${ticker} → review the daily/weekly chart, volume profile, and any recent news yourself. This is an educational alert. Paper mode.`;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-200">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-12">
          <div className="inline-block px-3 py-1 rounded-full bg-blue-950 text-blue-400 text-sm font-mono mb-4">
            PERSONAL LEARNING PROJECT
          </div>
          <h1 className="text-5xl font-semibold tracking-tighter mb-3">
            US AI/Tech Evening Scanner
          </h1>
          <p className="text-xl text-zinc-400 max-w-2xl">
            Friction-first alerts for the evening window. Educational only.{" "}
            <span className="text-emerald-400">Paper mode by default.</span>
          </p>
          <div className="mt-4 text-sm text-amber-400/80 font-mono">
            SEPARATE REPO • NOT part of the frozen SEMIS_MOM_CONF test
          </div>
        </div>

        {/* Safety Banner */}
        <div className="mb-10 rounded-2xl border border-amber-900/50 bg-amber-950/30 p-6 text-sm leading-relaxed">
          <div className="font-semibold text-amber-300 mb-2">Safety &amp; Scope</div>
          <ul className="list-disc pl-5 space-y-1 text-amber-200/90">
            <li>This app and the scanner exist in their own GitHub repository.</li>
            <li>No connection to the pre-registered frozen forward paper test on Alpaca.</li>
            <li>Alerts deliberately require you to open Robinhood yourself and make your own decision.</li>
            <li>Most retail systematic strategies have no edge net of costs. This is for practicing the loop, not for live capital.</li>
          </ul>
        </div>

        {/* Main actions */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-8">
            <div className="uppercase tracking-[2px] text-xs text-zinc-500 mb-3">LIVE ALERTS</div>
            <div className="text-2xl font-semibold mb-4">Discord is the primary surface</div>
            <p className="text-zinc-400 mb-6">
              When the scheduled scanner (GitHub Actions, ~22:00 UTC Mon-Fri) finds a qualifying BNF setup,
              you receive a rich embed with ticker, exact filter values, full rationale captured at generation time, and the instruction to open Robinhood.
            </p>
            <div className="text-sm bg-zinc-950 border border-zinc-800 rounded-xl p-4 font-mono text-emerald-300">
              Check NVDA on Robinhood<br />
              Dev -6.8% below 20DMA | Vol 1.9x avg | RS vs QQQ +4.2%<br />
              Generated 2026-06-16 22:03:12 UTC
            </div>
          </div>

          <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-8 flex flex-col">
            <div className="uppercase tracking-[2px] text-xs text-zinc-500 mb-3">SIMULATOR (THIS UI)</div>
            <div className="text-2xl font-semibold mb-4 flex-1">Try the alert format instantly</div>

            <button
              onClick={runSimulatedScan}
              disabled={isScanning}
              className="mt-auto w-full py-4 rounded-2xl bg-white text-black font-semibold text-lg active:scale-[0.985] transition disabled:opacity-60"
            >
              {isScanning ? "Scanning..." : "Run Simulated Evening Scan"}
            </button>
            <p className="text-[10px] text-center text-zinc-500 mt-3">
              Client-side demo only. Real scans run in the GitHub Action and post to Discord.
            </p>
          </div>
        </div>

        {/* Recent / Simulated Signals */}
        <div className="mb-12">
          <div className="flex items-baseline justify-between mb-4">
            <div className="uppercase tracking-[2px] text-xs text-zinc-500">Recent Signals (Demo + Real History)</div>
            <div className="text-xs text-zinc-500">signals.jsonl is committed by the Action → visible in repo</div>
          </div>

          {signals.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-zinc-800 p-10 text-center text-zinc-400">
              No demo signals yet. Click the button above to simulate one.
            </div>
          ) : (
            <div className="space-y-4">
              {signals.map((s, idx) => (
                <div key={idx} className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="font-mono text-2xl font-semibold text-white">{s.ticker}</div>
                    <div className="text-emerald-400 text-sm px-2 py-0.5 rounded bg-emerald-950">EDUCATIONAL</div>
                  </div>

                  <div className="font-mono text-sm text-zinc-300 mb-4">{s.reason}</div>

                  <div className="text-sm leading-relaxed text-zinc-400 mb-5 whitespace-pre-wrap">
                    {s.rationale}
                  </div>

                  <div className="pt-4 border-t border-zinc-800 text-sm">
                    <span className="font-semibold text-white">Action:</span>{" "}
                    {exampleAction(s.ticker)}
                  </div>

                  <div className="mt-2 text-[10px] text-zinc-500 font-mono">
                    {new Date(s.timestamp).toLocaleString()} UTC • Paper mode • Review outcome in 24-48h
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Setup & Deployment */}
        <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-8 mb-8">
          <div className="text-xl font-semibold mb-4">Deploy &amp; Run</div>
          <ol className="list-decimal pl-6 space-y-3 text-sm text-zinc-300">
            <li>Create a <strong>new GitHub repository</strong> (recommended — keep this completely separate from your frozen test repo).</li>
            <li>Push this project to it.</li>
            <li>In GitHub → Settings → Secrets and variables → Actions, add secret <code className="font-mono bg-black/50 px-1">DISCORD_WEBHOOK_URL</code>.</li>
            <li>Go to Vercel → New Project → Import the GitHub repo → Deploy. The Next.js UI is now live on Vercel.</li>
            <li>Go to the Actions tab in GitHub and manually trigger “Personal Evening AI/Tech Scanner” once to test.</li>
            <li>Optional: set repo variable <code className="font-mono bg-black/50 px-1">AI_TECH_UNIVERSE</code> to change the watchlist.</li>
          </ol>
          <p className="text-xs text-zinc-500 mt-6">
            The scheduled job (cron) lives in <code>.github/workflows/evening-ai-scan.yml</code>. It follows the same reliable pattern as the daily frozen tick runner in the main project.
          </p>
        </div>

        <footer className="text-center text-xs text-zinc-500 pt-8 border-t border-zinc-800">
          Educational tool only. Not financial advice. Practice journaling outcomes. Grind the real frozen test in the other repo.
        </footer>
      </div>
    </div>
  );
}
