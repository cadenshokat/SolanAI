from twscrape.accounts_pool import AccountsPool
import asyncio
from twitter_accounts import accounts
from tweet_scraper import load_cookies_from_file


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


if __name__ == "__main__":
    username = ""
    asyncio.run(delete(username))