from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
)


class SolscanClient:
    def __init__(
        self,
        base_url: str = "https://api-v2.solscan.io",
        cookie: Optional[str] = None,
        sol_aut: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout_s: float = 12.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.session = requests.Session()

        cookie = cookie or os.getenv("SOLSCAN_COOKIE", "")
        sol_aut = sol_aut or os.getenv("SOLSCAN_AUTH", "")
        user_agent = user_agent or os.getenv("SOLSCAN_UA", DEFAULT_UA)

        self._base_headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "user-agent": user_agent,
            "referer": "https://solscan.io/",
            "origin": "https://solscan.io",
            "connection": "keep-alive",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "sol-Aut": sol_aut,
            "cookie": cookie,
        }

    def _get(self, path: str, **params: Any) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = self.session.get(url, headers=self._base_headers, params=params, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()

    def account_transfers(
        self,
        address: str,
        page: int = 1,
        page_size: int = 30,
        remove_spam: bool = True,
        exclude_amount_zero: bool = True,
    ) -> List[Dict[str, Any]]:
        data = self._get(
            "/v2/account/transfer",
            address=address,
            page=page,
            page_size=page_size,
            remove_spam=str(remove_spam).lower(),
            exclude_amount_zero=str(exclude_amount_zero).lower(),
        )
        return data.get("data", []) or []
