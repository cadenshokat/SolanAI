from __future__ import annotations

import os
from typing import Any, Dict, List
import requests


def _format_large_number(n: int) -> str:
    num = int(n)
    if num < 1_000:
        return f"{num:,}"
    for div, suffix in [(1_000, "k"), (1_000_000, "m"), (1_000_000_000, "b"), (1_000_000_000_000, "t")]:
        if num < div * 1000:
            val = num / div
            s = f"{val:.2f}".rstrip("0").rstrip(".")
            return f"{s}{suffix}"
    val = num / 1_000_000_000_000
    s = f"{val:.2f}".rstrip("0").rstrip(".")
    return f"{s}t"


def get_coin_data(address: str) -> Dict[str, Any]:
    """
    Fetch coin metadata for a Solana token from CoinGecko by contract address.
    Env: COINGECKO_API_KEY (optional)
    """
    api_key = os.getenv("COINGECKO_API_KEY", None)
    headers = {"accept": "application/json"}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key

    url = f"https://api.coingecko.com/api/v3/coins/solana/contract/{address}"
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()

    image = (data.get("image") or {}).get("thumb")
    market_cap = (data.get("market_data") or {}).get("market_cap", {}).get("usd", 0) or 0
    community = data.get("community_data") or {}
    followers = community.get("twitter_followers", 0) or 0

    return {
        "image": image,
        "name": data.get("name"),
        "ticker": data.get("symbol"),
        "market_cap": _format_large_number(int(market_cap)),
        "twitter_followers": followers,
    }


def get_multiple_coin_data(addresses: List[str]) -> List[Dict[str, Any]]:
    """
    Dexscreener bulk metadata for multiple Solana token addresses.
    """
    if not addresses:
        return []
    addresses_str = ",".join(addresses)
    url = f"https://api.dexscreener.com/tokens/v1/solana/{addresses_str}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    payload = r.json() or []

    out: List[Dict[str, Any]] = []
    for coin in payload:
        info = coin.get("info") or {}
        socials = info.get("socials") or []
        twitter_url = ""
        for s in socials:
            if (s or {}).get("type") == "twitter":
                twitter_url = s.get("url") or ""
                break
        base = coin.get("baseToken") or {}
        out.append(
            {
                "image": info.get("imageUrl"),
                "name": base.get("name"),
                "ticker": base.get("symbol"),
                "market_cap": _format_large_number(int(coin.get("marketCap", 0) or 0)),
                "twitter": twitter_url,
                "age": coin.get("pairCreatedAt"),
            }
        )
    return out
