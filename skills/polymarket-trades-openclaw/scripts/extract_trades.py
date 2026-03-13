#!/usr/bin/env python3
"""Skill-local entrypoint for Polymarket trade extraction."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools" / "openclaw" / "polymarket_trade_extractor.py"

if not TOOL.exists():
    raise SystemExit(f"Tool script not found: {TOOL}")

spec = importlib.util.spec_from_file_location("polymarket_trade_extractor", TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sys.exit(mod.main())
