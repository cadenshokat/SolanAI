from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from ..clients.twscrape_pool import _cookies_path  # reuse path helper


def capture_cookies_via_browser(username: str) -> None:
    driver_path = os.getenv("CHROMEDRIVER_PATH")
    if not driver_path:
        raise RuntimeError("CHROMEDRIVER_PATH env var is required for Selenium cookie capture.")

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://twitter.com/login")
        print("A browser window opened. Log in to your X (Twitter) account there.")
        input("Press Enter here after you have fully logged in...")

        cookies: List[Dict[str, Any]] = driver.get_cookies()
        out = _cookies_path(username)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(cookies, indent=2))
        print(f"Cookies saved to {out}")
    finally:
        driver.quit()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m app.cli.capture_twitter_cookies <username>")
        raise SystemExit(2)
    capture_cookies_via_browser(sys.argv[1])
