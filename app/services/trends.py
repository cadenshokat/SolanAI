from __future__ import annotations

import asyncio
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from twscrape import API, gather

from ..core.config import settings
from .twitter_accounts import add_account, delete_account


# -------------------
# DB (separate file, per your existing pattern)
# -------------------

def _connect_trends_db() -> sqlite3.Connection:
    # Uses settings.TRENDS_DB (default: "trend_scraper/trending_data.db")
    path = settings.TRENDS_DB
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trending (
            run_time TEXT PRIMARY KEY,   -- ISO8601 timestamp
            topics   TEXT NOT NULL       -- JSON list
        )
    """)
    return conn


def _insert_trends(when: datetime, topics: List[str]) -> None:
    iso = when.replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    payload = json.dumps(topics)
    conn = _connect_trends_db()
    try:
        conn.execute(
            "REPLACE INTO trending(run_time, topics) VALUES (?, ?)",
            (iso, payload),
        )
        conn.commit()
    finally:
        conn.close()


def _latest_row() -> Optional[sqlite3.Row]:
    conn = _connect_trends_db()
    try:
        row = conn.execute(
            "SELECT run_time, topics FROM trending ORDER BY run_time DESC LIMIT 1"
        ).fetchone()
        return row
    finally:
        conn.close()


# -------------------
# Public Read API (used by /api/trending route)
# -------------------

def get_trending() -> Dict[str, Any]:
    row = _latest_row()
    if not row:
        return {"timestamp": None, "trending_topics": []}
    return {"timestamp": row["run_time"], "trending_topics": json.loads(row["topics"])}


def needs_update(hours: int = 1) -> bool:
    row = _latest_row()
    if not row:
        return True
    dt = datetime.strptime(row["run_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt) > timedelta(hours=hours)


# -------------------
# Ingest (refactor of your get_trends.py)
# -------------------

async def _fetch_trending_topics_async(account_username: str) -> None:
    """
    Adds the twscrape account (via cookies), calls `api.trends`, stores results, then removes account.
    Env:
      TW_ACCOUNTS_PY or TW_ACCOUNTS_FILE (handled by twitter_accounts service)
    """
    api = API()
    await add_account(account_username)

    try:
        # Your original logic used `search_trend = "trending"` with gather(...)
        # Keep parity with that behavior:
        topics_objs = await gather(api.trends("trending"))
        topics = [t.name for t in topics_objs] if topics_objs else []
        _insert_trends(datetime.now(timezone.utc), topics)
    finally:
        try:
            await delete_account(account_username)
        except Exception:
            pass


def refresh_trends() -> None:
    """
    Sync wrapper for scheduler or on-demand calls.
    Uses settings.TRENDS_USER (env) for the account key.
    """
    username = settings.TRENDS_USER
    if not username:
        raise RuntimeError("TRENDS_USER not configured.")
    asyncio.run(_fetch_trending_topics_async(username))
