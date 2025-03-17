import asyncio
import time
from tweet_scraper import load_cookies_from_file
from twitter_accounts import accounts
from textblob import TextBlob
from datetime import datetime, timedelta, timezone
from twscrape import API
import sqlite3
from twitter_accounts_init_delete import add, delete

def test_process_tweet_data(account_name):
    """Test the tweet data processing function."""

    async def run_test():
        api = API()


        account_info = accounts.get(account_name)
        await add(account_name)


        search_query = "$TRUMP"
        interval_minutes = 3

        """Fetch tweets, store data, and calculate percent change in one efficient function."""

        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        total_engagements = 0
        total_posts = 0
        sentiment_summary = {"positive": 0, "neutral": 0, "negative": 0}

        try:
            print(f"[DEBUG] Twitter API call #: Searching '{search_query}' with limit=500")

            async for tweet in api.search(search_query, limit=500):
                tweet_time = tweet.date
                if tweet_time > one_hour_ago:
                    engagement_score = tweet.likeCount + tweet.replyCount + tweet.retweetCount
                    total_engagements += engagement_score
                    total_posts += 1
                    text = tweet.rawContent
                    if text:
                        sentiment = TextBlob(text).sentiment.polarity
                        if sentiment > 0:
                            sentiment_summary["positive"] += 1
                        elif sentiment == 0:
                            sentiment_summary["neutral"] += 1
                        else:
                            sentiment_summary["negative"] += 1

            conn = sqlite3.connect("tweet_data.db")
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS tweet_metrics (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                coin TEXT,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                posts INTEGER,
                                engagements INTEGER)''')
            cursor.execute("INSERT INTO tweet_metrics (coin, posts, engagements) VALUES (?, ?, ?)",
                           (search_query, total_posts, total_engagements))
            conn.commit()

            time_threshold = datetime.now() - timedelta(minutes=interval_minutes)
            time_threshold_str = time_threshold.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                SELECT posts, engagements 
                FROM tweet_metrics 
                WHERE coin = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 2
                """, (search_query, time_threshold_str))
            rows = cursor.fetchall()
            conn.close()

            if len(rows) < 2:
                percent_changes = "Not enough data to calculate change."
            else:
                latest_data, earlier_data = rows[0], rows[1]
                posts_change_3m = ((latest_data[0] - earlier_data[0]) / earlier_data[0]) * 100 if earlier_data[
                                                                                                          0] > 0 else 0
                engagements_change_3m = ((latest_data[1] - earlier_data[1]) / earlier_data[1]) * 100 if \
                earlier_data[1] > 0 else 0
                percent_changes = {
                    "posts_change_percent": posts_change_3m,
                    "engagements_change_percent": engagements_change_3m
                }
        except Exception as e:
            print(f"Error while processing tweets: {e}")
            return None

        await delete(account_name)

        result = {
            "coin": search_query,
            "total_posts": total_posts,
            "total_engagements": total_engagements,
            "sentiment_summary": sentiment_summary,
            "percent_changes": percent_changes
        }



        # Assertions to validate the function output
        assert result is not None, "Function returned None, expected a dictionary."
        assert isinstance(result, dict), "Expected result to be a dictionary."
        assert "total_posts" in result and isinstance(result["total_posts"], int), "Total posts should be an integer."
        assert "total_engagements" in result and isinstance(result["total_engagements"],
                                                            int), "Total engagements should be an integer."
        assert "sentiment_summary" in result and isinstance(result["sentiment_summary"],
                                                            dict), "Sentiment summary should be a dictionary."
        assert "percent_changes" in result, "Percent changes key is missing."

        print("Test passed successfully!")
        print(f"Results: {result}")

    asyncio.run(run_test())


if __name__ == "__main__":
    while True:
        for account in accounts:
            test_process_tweet_data(account)
            print("Waiting for 3 minutes before next run...")
            time.sleep(180)
