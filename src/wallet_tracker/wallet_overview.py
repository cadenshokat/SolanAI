from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_wallet_7d_metrics(wallet_address):
    # Construct the URL for the wallet page on birdeye.so
    url = f"https://birdeye.so/profile/{wallet_address}?chain=solana"

    # Set up Chrome options for headless browsing
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service("/Users/cadenshokat/Downloads/chromedriver-mac-x64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    })

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)

        # Retrieve 7d PnL (handling both positive and negative cases)
        try:
            pnl_element = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span.text-success.text-title-medium-20")))
        except Exception:
            pnl_element = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span.text-destructive.text-title-medium-20")))
        pnl_text = pnl_element.text

        # Retrieve 7d Volume - update the CSS selector below to match the actual page element
        try:
            volume_element = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span.text-title-medium-20")))
        except Exception:
            volume_element = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span.text-title-medium-20")))  # try an alternate selector if needed
        volume_text = volume_element.text

        print(f"7d PnL: {pnl_text}")
        print(f"7d Volume: {volume_text}")

        return {"7d PnL": pnl_text, "7d Volume": volume_text}

    except Exception as e:
        print(f"Error retrieving metrics: {e}")
        return None
    finally:
        driver.quit()


if __name__ == "__main__":
    wallet_address = "BeTvN1ucBnCj4Ef688i51KHn2oq35CWDvD2J5aLFp17t"
    metrics = get_wallet_7d_metrics(wallet_address)
    if metrics:
        print(f"Metrics for wallet {wallet_address}: {metrics}")
    else:
        print("Failed to retrieve metrics.")
