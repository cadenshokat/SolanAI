from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from textblob import TextBlob
from twscrape import API

from ..db import tweet_store
from .twitter_accounts import add_account, delete_account


tweet_store.init()


async def _fetch_and_aggregate(
    account_username: str, search_query: str, lookback_minutes: int = 60, limit: int = 500
) -> Dict[str, Any]:
    """
    Uses a twscrape account (added via cookies) to search and aggregate metrics.
    - Totals posts/engagements over the last hour (default)
    - Basic sentiment tally (TextBlob)
    - Stores the snapshot into DB
    - Computes percent change vs a row ~= lookback window / 2 (latest two within window)

    Returns a dict with the computed fields.
    """
    api = API()

    # Ensure the account exists in the pool for this run
    await add_account(account_username)

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=lookback_minutes)

    total_engagements = 0
    total_posts = 0
    sentiment_summary = {"positive": 0, "neutral": 0, "negative": 0}

    try:
        async for tweet in api.search(search_query, limit=limit):
            tweet_time = getattr(tweet, "date", None)
            if not tweet_time or tweet_time <= window_start:
                continue

            like_count = int(getattr(tweet, "likeCount", 0) or 0)
            reply_count = int(getattr(tweet, "replyCount", 0) or 0)
            retweet_count = int(getattr(tweet, "retweetCount", 0) or 0)
            engagement = like_count + reply_count + retweet_count

            total_engagements += engagement
            total_posts += 1

            text = getattr(tweet, "rawContent", "") or ""
            if text:
                polarity = TextBlob(text).sentiment.polarity
                if polarity > 0:
                    sentiment_summary["positive"] += 1
                elif polarity == 0:
                    sentiment_summary["neutral"] += 1
                else:
                    sentiment_summary["negative"] += 1

        # persist snapshot
        tweet_store.insert_metric(search_query, total_posts, total_engagements, ts=now)

        # compare last two points within lookback/2 (e.g., 30 min if lookback=60)
        compare_minutes = max(3, lookback_minutes // 2)
        rows = tweet_store.latest_two_within(search_query, since_minutes=compare_minutes)
        if len(rows) < 2:
            percent_changes = "Not enough data to calculate change."
        else:
            (posts_now, eng_now), (posts_prev, eng_prev) = rows[0], rows[1]
            posts_change = ((posts_now - posts_prev) / posts_prev) * 100 if posts_prev > 0 else 0.0
            eng_change = ((eng_now - eng_prev) / eng_prev) * 100 if eng_prev > 0 else 0.0
            percent_changes = {
                "posts_change_percent": posts_change,
                "engagements_change_percent": eng_change,
            }

        await delete_account(account_username)

        return {
            "coin": search_query,
            "total_posts": total_posts,
            "total_engagements": total_engagements,
            "sentiment_summary": sentiment_summary,
            "percent_changes": percent_changes,
        }

    except Exception as e:
        print(e)


def run_search_job(
    account_username: str, search_query: str, lookback_minutes: int = 60, limit: int = 500
) -> Dict[str, Any]:
    """
    Sync wrapper so you can schedule this with our BackgroundScheduler.
    """
    return asyncio.run(_fetch_and_aggregate(account_username, search_query, lookback_minutes, limit))
