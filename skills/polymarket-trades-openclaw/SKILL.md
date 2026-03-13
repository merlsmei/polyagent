---
name: polymarket-trades-openclaw
description: Extract and analyze Polymarket trades from the past X hours for all active prediction markets, and format the results for OpenClaw tool workflows. Use when a user asks for recent trade activity, market-wide trade pulls, or automation-ready Polymarket trade exports.
---

# Polymarket Trades for OpenClaw

Use the bundled script to collect recent trades across active Polymarket markets.

## Workflow

1. Validate the requested time window (`--hours`) and output path.
2. Run the extractor script.
3. Verify non-empty output and summarize `tradeCount` and `marketCountScanned`.
4. Return or post-process the generated JSON for the caller.

## Commands

Run from this skill directory or adapt absolute paths:

```bash
python scripts/extract_trades.py --hours 6 --output /tmp/polymarket_trades_6h.json
```

Print to stdout instead of writing a file:

```bash
python scripts/extract_trades.py --hours 6 --output -
```

## Output contract

The tool emits a JSON object with:

- `since`: ISO timestamp start for the trailing window.
- `hours`: user-provided hour window.
- `marketCountScanned`: number of active markets queried.
- `tradeCount`: number of trades returned.
- `trades`: array of trade objects with `marketQuestion`, `marketSlug`, and `conditionId` enrichment.

## Notes

- The script uses public Polymarket APIs (`gamma-api` and `data-api`).
- For larger windows, increase `--market-max-pages` and keep a small `--pause-ms` to be polite to the API.
