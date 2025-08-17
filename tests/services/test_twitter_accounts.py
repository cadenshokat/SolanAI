import datetime as dt


def test_run_search_job_aggregates_and_persists(monkeypatch, tmp_path):
    from app.services import twitter_accounts as svc

    async def fake_add(_):
        return None

    async def fake_del(_):
        return None

    monkeypatch.setattr(svc, "add_account", fake_add)
    monkeypatch.setattr(svc, "delete_account", fake_del)

    now = dt.datetime.now(dt.timezone.utc)

    class Tweet:
        def __init__(self, when, likes, replies, rts, text):
            self.date = when
            self.likeCount = likes
            self.replyCount = replies
            self.retweetCount = rts
            self.rawContent = text

    async def gen():
        yield Tweet(now - dt.timedelta(minutes=10), 5, 1, 2, "great project")  # positive
        yield Tweet(now - dt.timedelta(minutes=30), 1, 0, 0, "meh")  # neutral-ish
        yield Tweet(now - dt.timedelta(minutes=50), 2, 1, 0, "bad idea")  # negative
        yield Tweet(now - dt.timedelta(hours=3), 50, 10, 10, "old")  # too old

    class FakeAPI:
        async def search(self, q, limit=500):
            async for t in gen():
                yield t

    monkeypatch.setattr(svc, "API", lambda: FakeAPI())

    snapshots = []

    class FakeStore:
        @staticmethod
        def init():
            pass

        @staticmethod
        def insert_metric(coin, posts, engagements, ts):
            snapshots.append((coin, posts, engagements, ts))

        @staticmethod
        def latest_two_within(coin, since_minutes):
            return [(10, 100), (5, 50)]  # now, prev

    monkeypatch.setattr(svc, "tweet_store", FakeStore)

    out = svc.run_search_job("acct", "$TEST", lookback_minutes=60, limit=500)
    assert out["coin"] == "$TEST"
    assert out["total_engagements"] == 12
    assert out["total_posts"] == 3
    assert set(out["sentiment_summary"].keys()) == {"positive", "neutral", "negative"}
    assert "percent_changes" in out and isinstance(out["percent_changes"], dict)
    assert snapshots and snapshots[-1][0] == "$TEST"


def test_run_search_job_not_enough_data(monkeypatch):
    from app.services import twitter_accounts as svc

    async def fake_add(_):
        return None

    async def fake_del(_):
        return None

    monkeypatch.setattr(svc, "add_account", fake_add)
    monkeypatch.setattr(svc, "delete_account", fake_del)

    class FakeAPI:
        async def search(self, q, limit=500):
            if False:
                yield
            return
            yield

    monkeypatch.setattr(svc, "API", lambda: FakeAPI())

    class FakeStore:
        @staticmethod
        def init():
            pass

        @staticmethod
        def insert_metric(coin, posts, engagements, ts):
            pass

        @staticmethod
        def latest_two_within(coin, since_minutes):
            return [(1, 10)]

    monkeypatch.setattr(svc, "tweet_store", FakeStore)

    out = svc.run_search_job("acct", "$ONE", lookback_minutes=60)
    assert out["percent_changes"] == "Not enough data to calculate change."
