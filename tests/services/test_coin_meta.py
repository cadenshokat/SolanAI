import json
import os


def test_get_coin_data_formats_and_uses_key(mock_http, monkeypatch):
    # Ensure env key is set so header gets added
    monkeypatch.setenv("COINGECKO_API_KEY", "demo-key")

    from app.services import coin_meta

    address = "SoMeToKeNaDdReSs"
    url = f"https://api.coingecko.com/api/v3/coins/solana/contract/{address}"

    mock_http.add(
        mock_http.GET,
        url,
        json={
            "image": {"thumb": "https://img.example/coin.png"},
            "name": "TestCoin",
            "symbol": "tst",
            "market_data": {"market_cap": {"usd": 435_490}},
            "community_data": {"twitter_followers": 12345},
        },
        status=200,
    )

    out = coin_meta.get_coin_data(address)
    assert out == {
        "image": "https://img.example/coin.png",
        "name": "TestCoin",
        "ticker": "tst",
        "market_cap": "435.49k",
        "twitter_followers": 12345,
    }

    assert len(mock_http.calls) == 1
    sent_headers = mock_http.calls[0].request.headers
    assert sent_headers.get("x-cg-demo-api-key") == "demo-key"


def test_get_multiple_coin_data_parses_list(mock_http):
    from app.services import coin_meta

    addresses = ["A", "B"]
    addr_str = ",".join(addresses)
    url = f"https://api.dexscreener.com/tokens/v1/solana/{addr_str}"

    mock_http.add(
        mock_http.GET,
        url,
        json=[
            {
                "info": {
                    "imageUrl": "https://img.example/a.png",
                    "socials": [{"type": "twitter", "url": "https://x.com/coinA"}],
                },
                "baseToken": {"name": "CoinA", "symbol": "A"},
                "marketCap": 1_200_000,
                "pairCreatedAt": 1700000000000,
            },
            {
                "info": {"imageUrl": "https://img.example/b.png", "socials": []},
                "baseToken": {"name": "CoinB", "symbol": "B"},
                "marketCap": 12_345,
                "pairCreatedAt": 1700000001000,
            },
        ],
        status=200,
    )

    out = coin_meta.get_multiple_coin_data(addresses)
    assert out == [
        {
            "image": "https://img.example/a.png",
            "name": "CoinA",
            "ticker": "A",
            "market_cap": "1.2m",
            "twitter": "https://x.com/coinA",
            "age": 1700000000000,
        },
        {
            "image": "https://img.example/b.png",
            "name": "CoinB",
            "ticker": "B",
            "market_cap": "12.35k",
            "twitter": "",
            "age": 1700000001000,
        },
    ]
