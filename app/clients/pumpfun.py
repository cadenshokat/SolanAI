from __future__ import annotations

import os
from typing import Any, Dict, List

import requests

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)


class PumpFunClient:
    """
    Minimal client for advanced-api-v2.pump.fun.
    Headers come from env (so you can rotate UA/referer if needed):
      PUMPFUN_UA, PUMPFUN_REFERER
    """

    def __init__(
        self, base: str = "https://advanced-api-v2.pump.fun", timeout_s: float = 15.0
    ) -> None:
        self.base = base.rstrip("/")
        self.timeout_s = timeout_s
        self.session = requests.Session()

        self._headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": os.getenv("PUMPFUN_UA", DEFAULT_UA),
            "referer": os.getenv("PUMPFUN_REFERER", "https://pump.fun/"),
        }

    def _get(self, path: str, **params: Any) -> Any:
        url = f"{self.base}{path}"
        r = self.session.get(url, headers=self._headers, params=params, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()

    def list_new(self) -> List[Dict[str, Any]]:
        # /coins/list?sortBy=creationTime
        data = self._get("/coins/list", sortBy="creationTime")
        return data or []

    def about_to_graduate(self) -> List[Dict[str, Any]]:
        data = self._get("/coins/about-to-graduate")
        return data or []
