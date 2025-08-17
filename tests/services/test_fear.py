def test_fear_current(mock_http, monkeypatch):
    monkeypatch.setenv("CMC_API_KEY", "k")

    from app.services import fear

    mock_http.add(
        mock_http.GET,
        "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest",
        json={"data": {"value": 63, "value_classification": "Greed"}},
        status=200,
    )

    out = fear.current()
    assert out == {"value": 63, "name": "Greed"}


def test_fear_history(mock_http, monkeypatch):
    monkeypatch.setenv("CMC_API_KEY", "k")

    from app.services import fear

    mock_http.add(
        mock_http.GET,
        "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical",
        json={"data": [{"timestamp": 1710, "value": 40}, {"timestamp": 1711, "value": 42}]},
        status=200,
    )

    out = fear.history()
    assert out == {1710: 40, 1711: 42}
