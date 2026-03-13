#!/usr/bin/env python3
"""OpenClaw-compatible tool for extracting recent Polymarket trades.

This script fetches active markets from Polymarket's Gamma API and then
collects trades from the Data API within a user-defined trailing time window.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

GAMMA_BASE = "https://gamma-api.polymarket.com"
DATA_BASE = "https://data-api.polymarket.com"
DEFAULT_TIMEOUT = 20


@dataclass
class Market:
    condition_id: str
    question: str
    slug: Optional[str]


def _get_json(url: str, timeout: int = DEFAULT_TIMEOUT):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "openclaw-polymarket-trade-extractor/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_active_markets(limit: int, max_pages: int, pause_ms: int) -> List[Market]:
    markets: List[Market] = []
    offset = 0

    for _ in range(max_pages):
        query = urllib.parse.urlencode(
            {
                "closed": "false",
                "active": "true",
                "archived": "false",
                "limit": str(limit),
                "offset": str(offset),
            }
        )
        url = f"{GAMMA_BASE}/markets?{query}"
        payload = _get_json(url)

        if not payload:
            break

        for item in payload:
            condition_id = item.get("conditionId")
            if condition_id:
                markets.append(
                    Market(
                        condition_id=condition_id,
                        question=item.get("question", ""),
                        slug=item.get("slug"),
                    )
                )

        if len(payload) < limit:
            break

        offset += limit
        if pause_ms > 0:
            time.sleep(pause_ms / 1000)

    # Deduplicate by condition_id while preserving order.
    seen = set()
    deduped: List[Market] = []
    for m in markets:
        if m.condition_id in seen:
            continue
        seen.add(m.condition_id)
        deduped.append(m)

    return deduped


def fetch_trades_for_market(condition_id: str, since_unix: int, limit: int, pause_ms: int) -> List[Dict]:
    all_trades: List[Dict] = []
    offset = 0

    while True:
        query = urllib.parse.urlencode(
            {
                "limit": str(limit),
                "offset": str(offset),
                "conditionId": condition_id,
            }
        )
        url = f"{DATA_BASE}/trades?{query}"
        payload = _get_json(url)
        if not payload:
            break

        reached_older = False
        for trade in payload:
            ts = trade.get("timestamp")
            if ts is None:
                continue
            if int(ts) < since_unix:
                reached_older = True
                continue
            all_trades.append(trade)

        if len(payload) < limit or reached_older:
            break

        offset += limit
        if pause_ms > 0:
            time.sleep(pause_ms / 1000)

    return all_trades


def enrich_trades(trades: Iterable[Dict], market: Market) -> Iterable[Dict]:
    for t in trades:
        out = dict(t)
        out["marketQuestion"] = market.question
        out["marketSlug"] = market.slug
        out["conditionId"] = market.condition_id
        yield out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract Polymarket trades from the past X hours.")
    p.add_argument("--hours", type=float, required=True, help="Trailing window in hours (e.g. 6, 24).")
    p.add_argument(
        "--output",
        default="-",
        help="Output path for JSON array results. Use '-' for stdout (default).",
    )
    p.add_argument("--market-page-size", type=int, default=200)
    p.add_argument("--market-max-pages", type=int, default=15)
    p.add_argument("--trade-page-size", type=int, default=500)
    p.add_argument("--pause-ms", type=int, default=50, help="Delay between API requests.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.hours <= 0:
        print("--hours must be > 0", file=sys.stderr)
        return 2

    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=args.hours)
    since_unix = int(since.timestamp())

    markets = fetch_active_markets(args.market_page_size, args.market_max_pages, args.pause_ms)

    results: List[Dict] = []
    for market in markets:
        try:
            trades = fetch_trades_for_market(
                condition_id=market.condition_id,
                since_unix=since_unix,
                limit=args.trade_page_size,
                pause_ms=args.pause_ms,
            )
        except Exception as exc:
            print(f"warning: failed to fetch {market.condition_id}: {exc}", file=sys.stderr)
            continue

        results.extend(enrich_trades(trades, market))

    output_text = json.dumps(
        {
            "since": since.isoformat(),
            "hours": args.hours,
            "marketCountScanned": len(markets),
            "tradeCount": len(results),
            "trades": results,
        },
        indent=2,
        sort_keys=True,
    )

    if args.output == "-":
        print(output_text)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Wrote {len(results)} trades to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
