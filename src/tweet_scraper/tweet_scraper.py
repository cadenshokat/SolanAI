
import json
import sqlite3

API_CALL_COUNT = 10

def load_cookies_from_file(account_name):
    """Load cookies from the saved file and convert to required format."""
    with open(f"tweet_scraper/cookies/cookies_{account_name}.json", "r") as file:
        cookies = json.load(file)
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    cookies_str = "; ".join(f"{name}={value}" for name, value in cookies_dict.items())
    return cookies_str

