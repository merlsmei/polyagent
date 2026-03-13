#!/usr/bin/env python3
"""Skill-local entrypoint for Polymarket trade extraction."""

from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools" / "openclaw" / "polymarket_trade_extractor.py"

if not TOOL.exists():
    raise SystemExit(f"Tool script not found: {TOOL}")

runpy.run_path(str(TOOL), run_name="__main__")
