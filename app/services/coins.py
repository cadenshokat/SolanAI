from __future__ import annotations

from threading import RLock
from typing import Any, Dict, List, Set

from ..clients.pumpfun import PumpFunClient
from ..db import coin_cache as cache
from ..services import wallets
from ..services.coin_meta import get_coin_data

cache.init()

_new_coins: List[Dict[str, Any]] = []
_almost_coins: List[Dict[str, Any]] = []
_nc_lock, _ac_lock = RLock(), RLock()


def _format_pump_coin(coin: Dict[str, Any]) -> Dict[str, Any]:
    timestamp_ms = coin.get("creationTime", 0) or 0
    ts = int(timestamp_ms // 1000)
    out = {
        "image": coin.get("imageUrl"),
        "name": coin.get("name"),
        "ticker": coin.get("ticker"),
        "age": ts,  # epoch seconds
        "market_cap": coin.get("marketCap"),
        "holders": coin.get("numHolders"),
        "volume": coin.get("volume"),
        "dev": coin.get("dev"),
        "address": coin.get("coinMint"),
        "red_flag": False,
    }

    holders = coin.get("holders") or []
    for h in holders:
        if h.get("holderId") == out["dev"]:
            if (h.get("ownedPercentage") or 0) > 5:
                out["red_flag"] = True
        if (h.get("ownedPercentage") or 0) < 20:
            out["red_flag"] = True

    if (out["volume"] or 0) < ((out["market_cap"] or 0) * 0.05):
        out["red_flag"] = True
    if (out["holders"] or 0) < 5:
        out["red_flag"] = True

    return out


def refresh_new_coins() -> None:
    client = PumpFunClient()
    raw = client.list_new()
    parsed = [_format_pump_coin(c) for c in (raw or [])]
    with _nc_lock:
        _new_coins.clear()
        _new_coins.extend(parsed)


def refresh_almost() -> None:
    client = PumpFunClient()
    raw = client.about_to_graduate()
    items: List[Dict[str, Any]] = []
    for coin in raw or []:
        ts = int((coin.get("creationTime", 0) or 0) / 1000)
        items.append(
            {
                "address": coin.get("coinMint"),
                "name": coin.get("name"),
                "ticker": coin.get("ticker"),
                "volume": coin.get("volume"),
                "market_cap": coin.get("marketCap"),
                "image": coin.get("imageUrl"),
                "holders": coin.get("numHolders"),
                "age": ts,
                "bonding_curve": coin.get("bondingCurveProgress"),
            }
        )
    with _ac_lock:
        _almost_coins.clear()
        _almost_coins.extend(items)


def get_new() -> List[Dict[str, Any]]:
    with _nc_lock:
        return list(_new_coins)


def get_almost() -> List[Dict[str, Any]]:
    with _ac_lock:
        return list(_almost_coins)


def _collect_candidate_tokens() -> Set[str]:
    # Enrich metadata for any tokens seen in recent transfers
    return wallets.get_candidate_tokens()


def refresh_coin_metadata() -> None:
    for t in _collect_candidate_tokens():
        if cache.get(t) is None:
            try:
                info = get_coin_data(t)
                cache.set(t, info)
            except Exception:
                pass


def get_cached_coins() -> Dict[str, Any]:
    return cache.get_all()
