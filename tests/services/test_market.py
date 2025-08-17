def test_fetch_sol_price_success(mock_http, monkeypatch, tmp_db):
    monkeypatch.setenv("BIRDEYE_API_KEY", "key")
    monkeypatch.setenv("DB_PATH", str(tmp_db))

    from app.db import sol_store

    sol_store.init()

    from app.services import market

    mock_http.add(
        mock_http.GET,
        "https://public-api.birdeye.so/defi/price",
        json={"data": {"value": 155.12, "updateUnixTime": 1710000000, "priceChange24h": 2.34}},
        status=200,
    )

    info = market.fetch_sol_price()
    assert info["price"] == 155.12
    assert info["timestamp"] == 1710000000
    assert info["dayChange"] == 2.34


def test_refresh_sol_price_persists_and_reads(mock_http, monkeypatch, tmp_db):
    monkeypatch.setenv("BIRDEYE_API_KEY", "key")
    monkeypatch.setenv("DB_PATH", str(tmp_db))

    from app.db import sol_store

    sol_store.init()

    from app.services import market

    mock_http.add(
        mock_http.GET,
        "https://public-api.birdeye.so/defi/price",
        json={"data": {"value": 100.0, "updateUnixTime": 1710001000, "priceChange24h": -1.0}},
        status=200,
    )

    market.refresh_sol_price()

    tl = market.get_sol_trendline()
    assert len(tl) == 1
    assert tl[0] == {"timestamp": 1710001000, "price": 100.0, "dayChange": -1.0}

    dc = market.get_daychange_from_timestamp(1710001000)
    assert dc == -1.0
