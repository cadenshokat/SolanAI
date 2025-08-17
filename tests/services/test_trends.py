def test_trends_refresh_and_get(monkeypatch, tmp_path):
    from app.services import trends

    monkeypatch.setattr(trends.settings, "TRENDS_DB", str(tmp_path / "trends.db"))
    monkeypatch.setattr(trends.settings, "TRENDS_USER", "acct1")

    class Trend:
        def __init__(self, name):
            self.name = name

    class FakeAPI:
        def trends(self, q):
            return [Trend("foo"), Trend("bar")]

    async def fake_gather(result):
        return result

    async def fake_add(_):
        return None

    async def fake_del(_):
        return None

    monkeypatch.setattr(trends, "API", lambda: FakeAPI())
    monkeypatch.setattr(trends, "gather", fake_gather)
    monkeypatch.setattr(trends, "add_account", fake_add)
    monkeypatch.setattr(trends, "delete_account", fake_del)

    trends.refresh_trends()
    out = trends.get_trending()
    assert out["trending_topics"] == ["foo", "bar"]
    assert out["timestamp"]

    assert trends.needs_update(hours=1000) is False


def test_trends_needs_update_true_when_empty(monkeypatch, tmp_path):
    from app.services import trends

    monkeypatch.setattr(trends.settings, "TRENDS_DB", str(tmp_path / "empty.db"))
    assert trends.needs_update(hours=1) is True
    assert trends.get_trending() == {"timestamp": None, "trending_topics": []}
