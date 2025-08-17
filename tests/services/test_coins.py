def test_refresh_new_coins_parses_and_flags(monkeypatch):
    from app.services import coins

    class FakePF:
        def list_new(self):
            return [{
                "creationTime": 1710000000000,
                "imageUrl": "i",
                "name": "Foo",
                "ticker": "FOO",
                "marketCap": 100000,
                "numHolders": 3,
                "volume": 1000,
                "dev": "dev1",
                "coinMint": "mint1",
                "holders": [{"holderId": "dev1", "ownedPercentage": 10}],
            }]

    monkeypatch.setattr(coins, "PumpFunClient", lambda: FakePF())

    coins.refresh_new_coins()
    out = coins.get_new()
    assert len(out) == 1
    c = out[0]
    assert c["name"] == "Foo"
    assert c["address"] == "mint1"
    assert c["age"] == 1710000000  # ms -> s
    assert c["red_flag"] is True


def test_refresh_almost(monkeypatch):
    from app.services import coins

    class FakePF:
        def about_to_graduate(self):
            return [{
                "creationTime": 1710001000000,
                "coinMint": "X",
                "name": "Bar",
                "ticker": "BAR",
                "volume": 5000,
                "marketCap": 500000,
                "imageUrl": "img",
                "numHolders": 12,
                "bondingCurveProgress": 0.8,
            }]

    monkeypatch.setattr(coins, "PumpFunClient", lambda: FakePF())

    coins.refresh_almost()
    out = coins.get_almost()
    assert len(out) == 1
    c = out[0]
    assert c["address"] == "X"
    assert c["age"] == 1710001000  # ms -> s
    assert c["bonding_curve"] == 0.8


def test_refresh_coin_metadata_calls_cache_set(monkeypatch):
    from app.services import coins

    monkeypatch.setattr(coins.wallets, "get_candidate_tokens", lambda: {"T1", "T2"})

    sets = []
    class FakeCache:
        @staticmethod
        def get(k): return None
        @staticmethod
        def set(k, v): sets.append((k, v))
        @staticmethod
        def get_all(): return {"T1": {"name": "X"}}

    monkeypatch.setattr(coins, "cache", FakeCache)

    monkeypatch.setattr(coins, "get_coin_data", lambda t: {"name": f"meta-{t}"})

    coins.refresh_coin_metadata()
    assert ("T1", {"name": "meta-T1"}) in sets
    assert ("T2", {"name": "meta-T2"}) in sets


def test_get_cached_coins_passthrough(monkeypatch):
    from app.services import coins

    monkeypatch.setattr(coins, "cache", type("C", (), {"get_all": staticmethod(lambda: {"A": 1})}))
    assert coins.get_cached_coins() == {"A": 1}
