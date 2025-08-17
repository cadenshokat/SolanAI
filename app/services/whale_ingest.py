from __future__ import annotations

import json
import re
import time
from typing import Dict, Any, List, Optional

import requests

from ..db import whale_store


SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"


def _rpc(method: str, params: list) -> Dict[str, Any]:
    r = requests.post(
        SOLANA_RPC_URL,
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def _get_latest_slot() -> int:
    return int(_rpc("getSlot", [{"commitment": "confirmed"}]).get("result", 0) or 0)


def _get_block_transactions(slot: int) -> List[Dict[str, Any]]:
    payload = _rpc(
        "getBlock",
        [
            slot,
            {
                "encoding": "json",
                "transactionDetails": "full",
                "rewards": False,
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0,
            },
        ],
    )
    result = payload.get("result") or {}
    return result.get("transactions") or []


def _extract_whale_buys(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Your original heuristic:
      - Look for token balance changes owned by spl-token account owner 5Q544f...
      - Treat SOL delta < -5 as a 'buy', collect mint + amount + signer.
    """
    out: Dict[str, Any] = {}
    for tx in transactions:
        txid = (tx.get("transaction") or {}).get("signatures", [None])[0]
        meta = tx.get("meta") or {}
        if meta.get("err") is not None:
            continue
        pre_bal = meta.get("preTokenBalances") or []
        post_bal = meta.get("postTokenBalances") or []
        signer = (tx.get("transaction") or {}).get("message", {}).get("accountKeys", [None])[0]

        pre_sol = 0.0
        post_sol = 0.0
        token = ""

        for pre in pre_bal:
            if pre.get("owner") == "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                if pre.get("mint") == "So11111111111111111111111111111111111111112":
                    pre_sol = (pre.get("uiTokenAmount") or {}).get("uiAmount", 0) or 0
                else:
                    token = pre.get("mint") or token

        for post in post_bal:
            if post.get("owner") == "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                if post.get("mint") == "So11111111111111111111111111111111111111112":
                    post_sol = (post.get("uiTokenAmount") or {}).get("uiAmount", 0) or 0
                else:
                    token = post.get("mint") or token

        delta = float(post_sol) - float(pre_sol)
        if delta < -5:  # buy > 5 SOL
            out[txid] = {"mint": token, "amount": abs(delta), "signer": signer}
    return out


def run_once() -> None:
    """
    Idempotent single tick:
      - Reads last processed slot from DB
      - Processes new slots up to latest
      - Writes any whale buys to DB with current timestamp
      - Persists last_slot
    """
    whale_store.init()
    last_slot = whale_store.get_last_slot()
    latest = _get_latest_slot()

    if last_slot is None:
        whale_store.set_last_slot(latest)
        return

    if latest <= last_slot:
        return

    aggregated: Dict[str, Any] = {}
    for slot in range(last_slot + 1, latest + 1):
        try:
            txs = _get_block_transactions(slot)
            found = _extract_whale_buys(txs)
            if found:
                aggregated.update(found)
        except Exception:
            # Swallow per-slot errors; continue
            continue

    if aggregated:
        ts = int(time.time())
        whale_store.save_transfers(ts, aggregated)

    whale_store.set_last_slot(latest)
