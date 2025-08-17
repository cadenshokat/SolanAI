from __future__ import annotations

from typing import Any, Dict, List, Optional

from .session import get_conn


def init() -> None:
    with get_conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS sol_cache (
                timestamp INTEGER PRIMARY KEY,
                price REAL NOT NULL,
                dayChange REAL NOT NULL
            )
            """
        )
        c.commit()


def upsert_point(timestamp: int, price: float, day_change: float) -> None:
    with get_conn() as c:
        c.execute(
            "REPLACE INTO sol_cache (timestamp, price, dayChange) VALUES (?, ?, ?)",
            (int(timestamp), float(price), float(day_change)),
        )
        c.commit()


def trendline() -> List[Dict[str, Any]]:
    with get_conn() as c:
        rows = c.execute(
            "SELECT timestamp, price, dayChange FROM sol_cache ORDER BY timestamp ASC"
        ).fetchall()
        return [
            {
                "timestamp": int(r["timestamp"]),
                "price": float(r["price"]),
                "dayChange": float(r["dayChange"]),
            }
            for r in rows
        ]


def daychange_at(timestamp: int) -> Optional[float]:
    with get_conn() as c:
        row = c.execute(
            "SELECT dayChange FROM sol_cache WHERE timestamp = ?", (int(timestamp),)
        ).fetchone()
        return float(row["dayChange"]) if row else None
