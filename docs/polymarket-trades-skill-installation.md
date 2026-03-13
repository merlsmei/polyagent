# Polymarket Trades Skill Installation Guide

This guide installs a local skill that uses an OpenClaw-compatible tool to pull Polymarket trades from the past _X_ hours.

## 1) Clone or enter the repository

```bash
git clone <your-repo-url> polyagent
cd polyagent
```

## 2) Verify Python

```bash
python3 --version
```

Use Python 3.9+.

## 3) Make scripts executable (optional)

```bash
chmod +x tools/openclaw/polymarket_trade_extractor.py
chmod +x skills/polymarket-trades-openclaw/scripts/extract_trades.py
```

## 4) Smoke test the tool directly

```bash
python3 tools/openclaw/polymarket_trade_extractor.py --hours 1 --output /tmp/polymarket_trades_1h.json
```

Expected behavior:
- exits with code `0`
- writes JSON with `tradeCount`, `marketCountScanned`, and `trades`

## 5) Run through the skill entrypoint

```bash
python3 skills/polymarket-trades-openclaw/scripts/extract_trades.py --hours 6 --output /tmp/polymarket_trades_6h.json
```

## 6) Register in OpenClaw (example)

Add a command-based tool registration in your OpenClaw tool config, pointing to:

```text
python3 /absolute/path/to/polyagent/tools/openclaw/polymarket_trade_extractor.py --hours {hours} --output -
```

Suggested tool metadata:
- name: `polymarket_recent_trades`
- parameter: `hours` (number, required)
- output: JSON object emitted on stdout

## 7) Validate output schema

```bash
python3 -m json.tool /tmp/polymarket_trades_6h.json | head -40
```

You should see top-level keys:
- `since`
- `hours`
- `marketCountScanned`
- `tradeCount`
- `trades`

## 8) Operational recommendations

- Start with `--hours 1` to validate quickly.
- For heavy usage, raise `--pause-ms` (e.g., 100–150) to reduce API pressure.
- For larger scans, increase `--market-max-pages`.
