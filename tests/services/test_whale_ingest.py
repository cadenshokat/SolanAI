def test_extract_whale_buys_basic():
    from app.services import whale_ingest as wi

    def tx(sol_before, sol_after, mint="MintX", signer="SigA"):
        return {
            "transaction": {"signatures": ["txid1"], "message": {"accountKeys": [signer]}},
            "meta": {
                "err": None,
                "preTokenBalances": [
                    {"owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
                     "mint": "So11111111111111111111111111111111111111112",
                     "uiTokenAmount": {"uiAmount": sol_before}},
                    {"owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
                     "mint": mint}
                ],
                "postTokenBalances": [
                    {"owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
                     "mint": "So11111111111111111111111111111111111111112",
                     "uiTokenAmount": {"uiAmount": sol_after}},
                    {"owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
                     "mint": mint}
                ],
            },
        }

    out = wi._extract_whale_buys([tx(100, 94, mint="TokenZ", signer="Alice")])
    assert "txid1" in out
    assert out["txid1"]["mint"] == "TokenZ"
    assert out["txid1"]["amount"] == 6.0
    assert out["txid1"]["signer"] == "Alice"

    out2 = wi._extract_whale_buys([tx(100, 97)])
    assert out2 == {}


def test_run_once_processes_new_slots(monkeypatch):
    from app.services import whale_ingest as wi

    calls = {"save": [], "set": []}

    class FakeStore:
        @staticmethod
        def init(): pass
        @staticmethod
        def get_last_slot(): return 10
        @staticmethod
        def set_last_slot(s): calls["set"].append(s)
        @staticmethod
        def save_transfers(ts, transfers): calls["save"].append((ts, transfers))

    monkeypatch.setattr(wi, "whale_store", FakeStore)

    monkeypatch.setattr(wi, "_get_latest_slot", lambda: 12)

    def txs(slot):
        if slot == 11:
            return [{
                "transaction": {"signatures": ["t11"], "message": {"accountKeys": ["S1"]}},
                "meta": {
                    "err": None,
                    "preTokenBalances": [
                        {"owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
                         "mint": "So11111111111111111111111111111111111111112",
                         "uiTokenAmount": {"uiAmount": 50}},
                    ],
                    "postTokenBalances": [
                        {"owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
                         "mint": "So11111111111111111111111111111111111111112",
                         "uiTokenAmount": {"uiAmount": 40}},
                        {"owner": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
                         "mint": "MintA"},
                    ],
                },
            }]
        return []

    monkeypatch.setattr(wi, "_get_block_transactions", txs)

    wi.run_once()

    assert calls["save"], "Expected at least one save_transfers call"
    assert calls["set"][-1] == 12
