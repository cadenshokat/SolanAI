from __future__ import annotations

import os
from typing import Any, Dict, List
import requests


_CMC_BASE = "https://pro-api.coinmarketcap.com/v3"
_TIMEOUT = 15


def _headers() -> Dict[str, str]:
    api_key = os.getenv("CMC_API_KEY") or os.getenv("COINMARKETCAP_API_KEY")
    if not api_key:
        raise RuntimeError("CMC_API_KEY (CoinMarketCap) not set")
    return {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }


def current() -> Dict[str, Any]:
    """
    Returns: {"value": <int or str>, "name": <classification>}
    """
    url = f"{_CMC_BASE}/fear-and-greed/latest"
    r = requests.get(url, headers=_headers(), timeout=_TIMEOUT)
    r.raise_for_status()
    data = (r.json() or {}).get("data") or {}
    return {
        "value": data.get("value"),
        "name": data.get("value_classification"),
    }


def history() -> Dict[str, Any]:
    """
    Returns a timestamp->value mapping (compatible with your old code).
    """
    url = f"{_CMC_BASE}/fear-and-greed/historical"
    r = requests.get(url, headers=_headers(), timeout=_TIMEOUT)
    r.raise_for_status()
    arr: List[Dict[str, Any]] = (r.json() or {}).get("data") or []
    out: Dict[str, Any] = {}
    for row in arr:
        ts = row.get("timestamp")
        val = row.get("value")
        if ts is not None:
            out[ts] = val
    return out
