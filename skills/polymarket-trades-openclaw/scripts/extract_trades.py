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
if spec is None or spec.loader is None:
    raise SystemExit(f"Unable to load tool script: {TOOL}")

mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
sys.exit(mod.main())
