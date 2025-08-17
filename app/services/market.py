from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

from ..db import sol_store

# Initialize table on import
sol_store.init()

_BIRDEYE_URL = "https://public-api.birdeye.so/defi/price"
_TIMEOUT = 12


def _birdeye_headers() -> Dict[str, str]:
    api_key = os.getenv("BIRDEYE_API_KEY")
    if not api_key:
        raise RuntimeError("BIRDEYE_API_KEY not set")
    return {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": api_key,
    }


def fetch_sol_price() -> Dict[str, Any]:
    """
    Hits Birdeye for SOL price. Uses the wrapped SOL mint by default.
    Env:
      SOL_MINT (optional) defaults to So11111111111111111111111111111111111111112
    Returns: {"price": float, "timestamp": int, "dayChange": float}
    """
    address = os.getenv("SOL_MINT", "So11111111111111111111111111111111111111112")
    r = requests.get(
        _BIRDEYE_URL, params={"address": address}, headers=_birdeye_headers(), timeout=_TIMEOUT
    )
    r.raise_for_status()
    data = (r.json() or {}).get("data") or {}
    return {
        "price": float(data.get("value") or 0.0),
        "timestamp": int(data.get("updateUnixTime") or 0),
        "dayChange": float(data.get("priceChange24h") or 0.0),
    }


def refresh_sol_price() -> None:
    """
    Fetches latest price and persists it into the sol_cache table.
    """
    info = fetch_sol_price()
    ts, price, dc = info["timestamp"], info["price"], info["dayChange"]
    if ts and price is not None:
        sol_store.upsert_point(ts, price, dc)


def get_sol_trendline() -> List[Dict[str, Any]]:
    return sol_store.trendline()


def get_daychange_from_timestamp(timestamp: int) -> Optional[float]:
    return sol_store.daychange_at(timestamp)
