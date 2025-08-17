from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any, Dict, List, Set

from app.clients.solscan import SolscanClient

from .wallet_metrics import get_wallet_7d_metrics

EXCLUDED_TOKENS: Set[str] = {
    "So11111111111111111111111111111111111111111",
    "So11111111111111111111111111111111111111112",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
}

_wallets: List[str] = []
_wallet_lock = RLock()

_tracker_cache: Dict[str, Any] = {"hot_buys": {}, "new_hot_buys": {}, "new_transfers": {}}
_tracker_lock = RLock()

_overview_cache: Dict[str, dict] = {}
_overview_lock = RLock()

_recent_transfers_cache: Dict[str, List[Dict[str, Any]]] = {}
_recent_transfers_lock = RLock()

# -------------------------
# API
# -------------------------


def update_wallets(wallets: List[str]) -> List[str]:
    wallets = [w for w in (wallets or []) if isinstance(w, str)][:10]
    with _wallet_lock:
        _wallets.clear()
        _wallets.extend(wallets)
    refresh_wallet_overview()
    return list(wallets)


def get_wallets() -> List[str]:
    with _wallet_lock:
        return list(_wallets)


def get_tracker_cache() -> Dict[str, Any]:
    with _tracker_lock:
        return {k: v for k, v in _tracker_cache.items()}


def get_overview_cache() -> Dict[str, dict]:
    with _overview_lock:
        return dict(_overview_cache)


def get_candidate_tokens() -> Set[str]:
    """Tokens seen in most-recent 'new_transfers' cache for metadata enrichment."""
    with _tracker_lock:
        new_transfers = _tracker_cache.get("new_transfers", {}) or {}
    tokens: Set[str] = set()
    for txs in new_transfers.values():
        for tx in txs:
            token = tx.get("token_address")
            if token:
                tokens.add(token)
    return tokens


# -------------------------
# SCHEDULED JOBS
# -------------------------


def refresh_wallet_tracker(min_wallets: int = 3) -> None:
    w = get_wallets()
    if not w:
        with _tracker_lock:
            _tracker_cache.update({"hot_buys": {}, "new_hot_buys": {}, "new_transfers": {}})
        return

    # Pull fresh transfers
    transfers_by_wallet = _get_recent_transfers(w)
    with _recent_transfers_lock:
        _recent_transfers_cache.clear()
        _recent_transfers_cache.update(transfers_by_wallet)

    hot_buys = _get_popular_tokens(transfers_by_wallet, min_wallets=min_wallets)
    new_hot_buys = _get_new_popular_tokens(
        transfers_by_wallet, min_wallets=min_wallets, within_minutes=5
    )
    new_transfers = _get_new_transfers(transfers_by_wallet, within_minutes=5)

    with _tracker_lock:
        _tracker_cache["hot_buys"] = hot_buys
        _tracker_cache["new_hot_buys"] = new_hot_buys
        _tracker_cache["new_transfers"] = new_transfers


def refresh_wallet_overview() -> None:
    w = get_wallets()
    if not w:
        return
    with _overview_lock:
        for wallet in w:
            try:
                metrics = get_wallet_7d_metrics(wallet) or {"7d PnL": "N/A", "7d Volume": "N/A"}
            except Exception:
                metrics = {"7d PnL": "Error", "7d Volume": "Error"}
            _overview_cache[wallet] = metrics


# -------------------------
# Core logic (refactor of wallet_tracker.py)
# -------------------------


def _get_recent_transfers(wallets: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    client = SolscanClient()
    out: Dict[str, List[Dict[str, Any]]] = {}
    for wallet in wallets:
        try:
            rows = client.account_transfers(
                wallet, page=1, page_size=30, remove_spam=True, exclude_amount_zero=True
            )
        except Exception:
            rows = []

        normalized: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc)
        for t in rows:
            if t.get("activity_type") != "ACTIVITY_SPL_TRANSFER":
                continue
            token = t.get("token_address")
            if not token or token in EXCLUDED_TOKENS:
                continue

            block_time = t.get("block_time")  # epoch seconds
            if not isinstance(block_time, (int, float)):
                continue
            dt = datetime.fromtimestamp(block_time, tz=timezone.utc)
            age_td = now - dt

            amount_raw = t.get("amount", 0) or 0
            decimals = t.get("token_decimals", 0) or 0
            try:
                amount = float(amount_raw) / (10 ** int(decimals))
            except Exception:
                amount = 0.0

            normalized.append(
                {
                    "transaction_id": t.get("trans_id"),
                    "token_address": token,
                    "amount": amount,
                    "age": str(age_td),  # keep string to match prior behavior
                    "activity_type": "ACTIVITY_SPL_TRANSFER",
                    "block_time": int(block_time),
                }
            )
        out[wallet] = normalized
    return out


def _parse_age_str(age_str: str) -> timedelta:
    parts = (age_str or "").split(", ")
    if len(parts) == 2:
        days = int(parts[0].split()[0])
        time_part = parts[1]
    else:
        days = 0
        time_part = parts[0] if parts else "0:00:00"
    hrs, mins, secs = time_part.split(":")
    return timedelta(days=days, hours=float(hrs), minutes=float(mins), seconds=float(secs))


def _get_new_transfers(
    wallet_transfers: Dict[str, List[Dict[str, Any]]],
    within_minutes: int = 5,
) -> Dict[str, List[Dict[str, Any]]]:
    cutoff = timedelta(minutes=within_minutes)
    result: Dict[str, List[Dict[str, Any]]] = {}
    for wallet, transfers in wallet_transfers.items():
        recent = []
        for t in transfers:
            try:
                age = _parse_age_str(t.get("age", "0:00:00"))
            except Exception:
                continue
            if age <= cutoff:
                recent.append(t)
        if recent:
            result[wallet] = recent
    return result


def _get_popular_tokens(
    wallet_transfers: Dict[str, List[Dict[str, Any]]],
    min_wallets: int = 2,
) -> Dict[str, int]:
    token_wallets: Dict[str, set] = defaultdict(set)
    for wallet, transfers in wallet_transfers.items():
        for t in transfers:
            token = t.get("token_address")
            if token:
                token_wallets[token].add(wallet)
    return {tok: len(ws) for tok, ws in token_wallets.items() if len(ws) >= min_wallets}


def _get_new_popular_tokens(
    wallet_transfers: Dict[str, List[Dict[str, Any]]],
    min_wallets: int = 2,
    within_minutes: int = 5,
) -> Dict[str, int]:
    cutoff = timedelta(minutes=within_minutes)
    token_wallets: Dict[str, set] = defaultdict(set)
    for wallet, transfers in wallet_transfers.items():
        for t in transfers:
            try:
                age = _parse_age_str(t.get("age", "0:00:00"))
            except Exception:
                continue
            if age <= cutoff:
                token = t.get("token_address")
                if token:
                    token_wallets[token].add(wallet)
    return {tok: len(ws) for tok, ws in token_wallets.items() if len(ws) >= min_wallets}
