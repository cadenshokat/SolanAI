from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .session import get_conn

_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS coin_cache (
  token_address TEXT PRIMARY KEY,
  coin_info     TEXT NOT NULL
);
"""


def init() -> None:
    with get_conn() as conn:
        conn.execute(_TABLE_SQL)
        conn.commit()


def get(token: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT coin_info FROM coin_cache WHERE token_address = ?",
            (token,),
        ).fetchone()
    if not row:
        return None
    try:
        return json.loads(row[0])
    except Exception:
        return None


def set(token: str, info: Dict[str, Any]) -> None:
    payload = json.dumps(info)
    with get_conn() as conn:
        conn.execute(
            "REPLACE INTO coin_cache(token_address, coin_info) VALUES (?, ?)",
            (token, payload),
        )
        conn.commit()


def get_all() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    with get_conn() as conn:
        rows = conn.execute("SELECT token_address, coin_info FROM coin_cache").fetchall()
    for token, payload in rows or []:
        try:
            out[token] = json.loads(payload)
        except Exception:
            continue
    return out
