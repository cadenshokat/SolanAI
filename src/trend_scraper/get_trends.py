import asyncio
import json
from datetime import datetime
from twscrape import API, gather
import sqlite3

# Import your account helpers (if needed)
from twscrape.accounts_pool import AccountsPool

accounts = {
    "trendy1490087": {
        "password": "trendy_cashcow_n001",
        "email": "cashcow.trendy001@mail.com",
        "email_password": "trendy_cashcow_n001",
        "cookies": "cookies_trendy1490087.json"
    },
    "mrtrends454970": {
        "password": "mrtrends_cashcow_n002",
        "email": "cashcow.mrtrends002@mail.com",
        "email_password": "mrtrends_cashcow_n002",
        "cookies": "cookies_mrtrends454970.json"
    }
}


def load_cookies_from_file(account_name):
    """Load cookies from the saved file and convert to required format."""
    with open(f"cookies/cookies_{account_name}.json", "r") as file:
        cookies = json.load(file)
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    cookies_str = "; ".join(f"{name}={value}" for name, value in cookies_dict.items())
    return cookies_str

pool = AccountsPool()


async def delete(username) :

    await pool.delete_accounts(username)
    print(f"{username} deleted")


async def add(username):
    account_info = accounts.get(username)

    try:
        print("[DEBUG] Adding account using cookies...")
        await pool.add_account(
            username,
            account_info.get("password"),
            account_info.get("email"),
            account_info.get("email_password"),
            cookies=load_cookies_from_file(username)
        )
        print("Account added successfully using cookies.")
    except Exception as e:
        print(f"Failed to add account: {e}")
        return


async def fetch_trending_topics(account_name):
    api = API()
    await add(account_name)

    search_trend = "trending"  # Query for trending topics
    try:
        print(f"[DEBUG] Twitter API call: Fetching trending topics")
        trends = await gather(api.trends(search_trend))  # returns list[Trend]

        # Extract list of trending topic names
        trending_topics = [trend.name for trend in trends]
        print("Fetched Trending Topics:")
        print(trending_topics)

        # Get current timestamp as the key
        run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Connect to (or create) the database for trending topics
        conn = sqlite3.connect("trending_data.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending (
                run_time DATETIME PRIMARY KEY,
                topics TEXT
            )
        ''')

        # Convert the list to a JSON string
        topics_json = json.dumps(trending_topics)

        # Insert the record with the current timestamp and the JSON list of topics
        cursor.execute(
            "INSERT INTO trending (run_time, topics) VALUES (?, ?)",
            (run_time, topics_json)
        )
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error while processing trending topics: {e}")
        return None

    await delete(account_name)
    print("Trending topics processed successfully.")

def test_trending_fetch(account_name):
    asyncio.run(fetch_trending_topics(account_name))

if __name__ == "__main__":
    test_trending_fetch("mrtrends454970")
