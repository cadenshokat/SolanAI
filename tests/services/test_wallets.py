import datetime as dt


def test_update_and_overview(monkeypatch):
    from app.services import wallets

    monkeypatch.setattr(
        wallets, "get_wallet_7d_metrics", lambda w: {"7d PnL": "1%", "7d Volume": "10k"}
    )

    updated = wallets.update_wallets(["A", "B", "C"])
    assert updated == ["A", "B", "C"]

    ov = wallets.get_overview_cache()
    assert ov["A"]["7d PnL"] == "1%"
    assert ov["B"]["7d Volume"] == "10k"


def test_get_recent_transfers_filters_and_parses(monkeypatch):
    from app.services import wallets

    now = int(dt.datetime.now(dt.timezone.utc).timestamp())

    rows = [
        {
            "activity_type": "ACTIVITY_SPL_TRANSFER",
            "token_address": "TOKEN1",
            "block_time": now - 60,
            "amount": 12345,
            "token_decimals": 3,
            "trans_id": "tx1",
        },
        {
            "activity_type": "OTHER",
            "token_address": "X",
            "block_time": now - 60,
            "amount": 1,
            "token_decimals": 0,
        },
        {
            "activity_type": "ACTIVITY_SPL_TRANSFER",
            "token_address": "So11111111111111111111111111111111111111112",
            "block_time": now - 60,
            "amount": 1,
            "token_decimals": 0,
        },
        {
            "activity_type": "ACTIVITY_SPL_TRANSFER",
            "token_address": "TOKEN2",
            "block_time": "bad",
            "amount": 1,
            "token_decimals": 0,
        },
    ]

    class FakeClient:
        def account_transfers(self, *a, **k):
            return rows

    from app.clients import solscan as solscan_mod

    monkeypatch.setattr(solscan_mod, "SolscanClient", lambda: FakeClient())

    out = wallets._get_recent_transfers(["W1"])
    assert "W1" in out
    txs = out["W1"]
    assert len(txs) == 1
    t = txs[0]
    assert t["token_address"] == "TOKEN1"
    assert t["amount"] == 12.345
    assert t["activity_type"] == "ACTIVITY_SPL_TRANSFER"


def test_refresh_wallet_tracker_and_candidates(monkeypatch):
    from app.services import wallets

    monkeypatch.setattr(wallets, "get_wallets", lambda: ["W1", "W2"])

    def fake_recent(_wallets):
        return {
            "W1": [
                {"token_address": "T", "age": "0:03:00", "activity_type": "ACTIVITY_SPL_TRANSFER"},
                {"token_address": "X", "age": "0:10:00", "activity_type": "ACTIVITY_SPL_TRANSFER"},
            ],
            "W2": [
                {"token_address": "T", "age": "0:02:00", "activity_type": "ACTIVITY_SPL_TRANSFER"},
            ],
        }

    monkeypatch.setattr(wallets, "_get_recent_transfers", fake_recent)

    wallets.refresh_wallet_tracker(min_wallets=2)

    cache = wallets.get_tracker_cache()
    assert cache["hot_buys"] == {"T": 2}
    assert cache["new_hot_buys"] == {"T": 2}
    assert "W2" in cache["new_transfers"] and "W1" in cache["new_transfers"]

    toks = wallets.get_candidate_tokens()
    assert "T" in toks
