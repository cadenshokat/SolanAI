from __future__ import annotations

import os
from typing import Dict, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def get_wallet_7d_metrics(wallet_address: str, timeout_s: int = 20) -> Optional[Dict[str, str]]:
    """
    Scrape 7d PnL + Volume from birdeye.so. Requires ChromeDriver.
    Env:
      CHROMEDRIVER_PATH: absolute path to chromedriver binary
      BIRDEYE_BASEURL:   defaults to https://birdeye.so
    """
    base = os.getenv("BIRDEYE_BASEURL", "https://birdeye.so")
    url = f"{base}/profile/{wallet_address}?chain=solana"
    driver_path = os.getenv("CHROMEDRIVER_PATH")
    if not driver_path:
        raise RuntimeError("CHROMEDRIVER_PATH env var is required for Selenium scraping.")

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_cdp_cmd(
        "Network.setUserAgentOverride",
        {
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        },
    )

    try:
        driver.get(url)
        wait = WebDriverWait(driver, timeout_s)

        # 7d PnL (positive uses 'text-success', negative 'text-destructive')
        pnl_sel_pos = "span.text-success.text-title-medium-20"
        pnl_sel_neg = "span.text-destructive.text-title-medium-20"
        pnl_el = None
        try:
            pnl_el = wait.until(ec.presence_of_element_located((By.ec, pnl_sel_pos)))
        except Exception:
            pnl_el = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, pnl_sel_neg)))
        pnl = pnl_el.text

        # 7d Volume — keep selector broad to tolerate UI changes
        vol_el = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "span.text-title-medium-20")))
        vol = vol_el.text

        return {"7d PnL": pnl, "7d Volume": vol}
    except Exception:
        return None
    finally:
        driver.quit()
