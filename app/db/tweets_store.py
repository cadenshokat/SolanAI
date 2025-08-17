from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from .session import get_conn


def init() -> None:
    with get_conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS tweet_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                ts TEXT NOT NULL,          -- ISO8601 in UTC
                posts INTEGER NOT NULL,
                engagements INTEGER NOT NULL
            )
            """
        )
        c.execute("CREATE INDEX IF NOT EXISTS idx_tweet_metrics_coin_ts ON tweet_metrics(coin, ts)")
        c.commit()


def insert_metric(coin: str, posts: int, engagements: int, ts: Optional[datetime] = None) -> None:
    ts = ts or datetime.now(timezone.utc)
    iso = ts.replace(tzinfo=timezone.utc).isoformat(timespec="seconds")
    with get_conn() as c:
        c.execute(
            "INSERT INTO tweet_metrics (coin, ts, posts, engagements) VALUES (?, ?, ?, ?)",
            (coin, iso, int(posts), int(engagements)),
        )
        c.commit()


def latest_two_within(coin: str, since_minutes: int) -> List[Tuple[int, int]]:
    """
    Returns up to 2 most recent rows (posts, engagements) for `coin`
    within the last `since_minutes`.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
    cutoff_iso = cutoff.replace(tzinfo=timezone.utc).isoformat(timespec="seconds")
    with get_conn() as c:
        rows = c.execute(
            """
            SELECT posts, engagements
            FROM tweet_metrics
            WHERE coin = ? AND ts >= ?
            ORDER BY ts DESC
            LIMIT 2
            """,
            (coin, cutoff_iso),
        ).fetchall()
        return [(int(r["posts"]), int(r["engagements"])) for r in rows]
