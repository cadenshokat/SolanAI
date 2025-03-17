import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def capture_cookies_via_browser(username):
    """Automates the login process to X and captures cookies."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service("/Users/cadenshokat/Downloads/chromedriver-mac-x64/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://twitter.com/login")
        print("Please log in to your X (Twitter) account in the opened browser.")
        input("Press Enter here in the terminal after you have logged in...")


        cookies = driver.get_cookies()
        with open(f"tweet_scraper/cookies/cookies_{username}.json", "w") as file:
            json.dump(cookies, file)
        print(f"Cookies captured and saved to 'cookies_{username}.json'.")
    finally:
        driver.quit()


if __name__ == "__main__":
    username = "cookie377906"
    capture_cookies_via_browser(username)