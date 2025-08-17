from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .session import get_conn


def init() -> None:
    with get_conn() as c:
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS whaleTransfers (
            timestamp INTEGER PRIMARY KEY,
            transfers TEXT NOT NULL
        )"""
        )
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS whaleMeta (
            k TEXT PRIMARY KEY,
            v TEXT
        )"""
        )
        c.commit()


def save_transfers(ts: int, transfers: Dict[str, Any]) -> None:
    payload = json.dumps(transfers)
    with get_conn() as c:
        c.execute("REPLACE INTO whaleTransfers(timestamp, transfers) VALUES(?, ?)", (ts, payload))
        c.commit()


def get_last_slot() -> Optional[int]:
    with get_conn() as c:
        row = c.execute("SELECT v FROM whaleMeta WHERE k='last_slot'").fetchone()
        return int(row["v"]) if row else None


def set_last_slot(slot: int) -> None:
    with get_conn() as c:
        c.execute("REPLACE INTO whaleMeta(k, v) VALUES('last_slot', ?)", (str(slot),))
        c.commit()
