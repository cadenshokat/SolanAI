from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from twscrape.accounts_pool import AccountsPool


def _cookies_path(username: str) -> Path:
    base = Path(os.getenv("TW_COOKIES_DIR", "tweet_scraper/cookies"))
    base.mkdir(parents=True, exist_ok=True)
    return base / f"cookies_{username}.json"


def load_cookies_from_file(username: str) -> Optional[List[Dict[str, Any]]]:
    p = _cookies_path(username)
    if not p.exists():
        return None
    return json.loads(p.read_text())


class TwscrapePool:
    """
    Manages the shared AccountsPool instance.
    Notes:
      - twscrape uses its own SQLite under the hood; we just add/delete accounts here.
      - We prefer cookie-based add to avoid interactive login.
    """

    def __init__(self) -> None:
        self.pool = AccountsPool()

    async def add_with_cookies(
        self, username: str, password: str, email: Optional[str], email_password: Optional[str]
    ) -> None:
        cookies = load_cookies_from_file(username)
        await self.pool.add_account(username, password, email, email_password, cookies=cookies)

    async def delete(self, username: str) -> None:
        await self.pool.delete_accounts(username)
