from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Dict, Any

from app.clients.twscrape_pool import TwscrapePool


def _accounts_from_py() -> Dict[str, Dict[str, Any]]:
    """
    Load accounts from a Python module providing a top-level `accounts: dict`.
    Env:
      TW_ACCOUNTS_PY (default "config.twitter_accounts")
    """
    module_path = os.getenv("TW_ACCOUNTS_PY", "config.twitter_accounts")
    try:
        mod = importlib.import_module(module_path)
        data = getattr(mod, "accounts", None)
        if not isinstance(data, dict):
            raise ValueError(f"{module_path}.accounts must be a dict")
        return data
    except ModuleNotFoundError:
        return {}


def _accounts_from_json() -> Dict[str, Dict[str, Any]]:
    """
    Fallback to JSON file if Python module isn't present.
    Env:
      TW_ACCOUNTS_FILE (default "tweet_scraper/twitter_accounts.json")
    """
    path = Path(os.getenv("TW_ACCOUNTS_FILE", "tweet_scraper/twitter_accounts.json"))
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _load_accounts() -> Dict[str, Dict[str, Any]]:
    data = _accounts_from_py()
    if data:
        return data
    data = _accounts_from_json()
    if data:
        return data
    raise FileNotFoundError(
        "No Twitter accounts found. Set TW_ACCOUNTS_PY to a module with `accounts` "
        "or TW_ACCOUNTS_FILE to a JSON file."
    )


async def add_account(username: str) -> None:
    accounts = _load_accounts()
    if username not in accounts:
        raise KeyError(f"Username '{username}' not found in configured accounts.")
    info = accounts[username]
    pool = TwscrapePool()
    await pool.add_with_cookies(
        username=username,
        password=info.get("password") or "",
        email=info.get("email"),
        email_password=info.get("email_password"),
    )


async def delete_account(username: str) -> None:
    pool = TwscrapePool()
    await pool.delete(username)
