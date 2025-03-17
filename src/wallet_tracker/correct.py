from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_wallet_7d_pnl(wallet_address):
    # Construct the URL for the wallet page on birdeye.so
    url = f"https://birdeye.so/profile/{wallet_address}?chain=solana"

    # Set up Chrome options for headless browsing
    options = Options()
    options.headless = True

    # Path to your ChromeDriver executable; update as needed.
    service = Service("/Users/cadenshokat/Downloads/chromedriver-mac-x64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    # Optional: Set a realistic user-agent to mimic a real browser.
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    })

    try:
        driver.get(url)

        # Wait for the DOM element that contains the 7d PnL to load.
        # You need to inspect the page to determine the correct CSS selector.
        # Here, we assume the element has a class "pnl-7d" (adjust as needed).
        wait = WebDriverWait(driver, 15)
        pnl_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.text-success.text-title-medium-20")))
        pnl_text = pnl_element.text

        return pnl_text

    except Exception as e:
        print("Error retrieving 7d PnL:", e)
        return None
    finally:
        driver.quit()


if __name__ == "__main__":
    wallet_address = "3Vsx9RN9jvnKwdMkHxn6Z2cehtffgghk4Kd4MStHT1P6"
    pnl = get_wallet_7d_pnl(wallet_address)
    if pnl:
        print(f"7d PnL for wallet {wallet_address}: {pnl}")
    else:
        print("Failed to retrieve 7d PnL data.")
