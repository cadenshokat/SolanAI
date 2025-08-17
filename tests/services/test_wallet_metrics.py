def test_get_wallet_7d_metrics_happy_path(monkeypatch):
    from app.services import wallet_metrics as wm

    monkeypatch.setenv("CHROMEDRIVER_PATH", "/tmp/chromedriver")

    class FakeEl:
        def __init__(self, text): self.text = text

    class FakeWait:
        def __init__(self, driver, timeout): pass
        def until(self, cond):
            if not hasattr(self, "_called"):
                self._called = 1
                return FakeEl("+12%")
            return FakeEl("$1.2M")

    class FakeDriver:
        def execute_cdp_cmd(self, *args, **kwargs): pass
        def get(self, url): self.url = url
        def quit(self): pass

    monkeypatch.setattr(wm.webdriver, "Chrome", lambda service, options: FakeDriver())
    monkeypatch.setattr(wm, "WebDriverWait", FakeWait)

    out = wm.get_wallet_7d_metrics("WALLET123")
    assert out == {"7d PnL": "+12%", "7d Volume": "$1.2M"}


def test_get_wallet_7d_metrics_returns_none_on_error(monkeypatch):
    from app.services import wallet_metrics as wm
    monkeypatch.setenv("CHROMEDRIVER_PATH", "/tmp/chromedriver")

    class FakeDriver:
        def execute_cdp_cmd(self, *args, **kwargs): pass
        def get(self, url): raise RuntimeError("boom")
        def quit(self): pass

    class FakeWait:
        def __init__(self, *a, **k): pass
        def until(self, c): return None

    monkeypatch.setattr(wm.webdriver, "Chrome", lambda service, options: FakeDriver())
    monkeypatch.setattr(wm, "WebDriverWait", FakeWait)

    assert wm.get_wallet_7d_metrics("W") is None
