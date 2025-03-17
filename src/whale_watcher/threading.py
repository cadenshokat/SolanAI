import requests
import time
import json
import base58
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Solana Mainnet RPC endpoint
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"


def get_latest_slot():
    response = requests.post(SOLANA_RPC_URL, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSlot",
        "params": [{"commitment": "confirmed"}]
    })
    return response.json().get("result", 0)


def get_transactions_in_block(slot):
    response = requests.post(SOLANA_RPC_URL, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlock",
        "params": [
            slot,
            {
                "encoding": "json",
                "transactionDetails": "full",
                "rewards": False,
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    })
    print(response.json())

    if response.status_code == 200:
        return response.json().get("result", {}).get("transactions", [])
    return []


def process_whale_transactions(transactions):
    for tx in transactions:
        transaction_id = tx.get("transaction", {}).get("signatures", [None])[0]
        meta = tx.get("meta", {})
        logs = meta.get("logMessages", [])
        messages = tx.get("transaction", {}).get("message", {})
        instructions = messages.get("instructions", [])
        pre_balances = meta.get("preTokenBalances", [])
        post_balances = meta.get("postTokenBalances", [])

        if meta.get('err') is None and pre_balances:
            """print(transaction_id)
            print(tx)"""

        # Only process if there is no error and there are token balances (as in your existing logic)




def main():
    print("🚀 Starting Solana RPC Listener...")
    last_slot = get_latest_slot()

    # Create a thread pool to parallelize HTTP requests.
    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            current_slot = get_latest_slot()

            if current_slot > last_slot:
                # Submit a task for each new slot that needs to be processed.
                future_to_slot = {
                    executor.submit(get_transactions_in_block, slot): slot
                    for slot in range(last_slot + 1, current_slot + 1)
                }

                # As each future completes, process its results.
                for future in as_completed(future_to_slot):
                    slot = future_to_slot[future]
                    try:
                        transactions = future.result()
                        process_whale_transactions(transactions)
                    except Exception as e:
                        print(f"Error processing slot {slot}: {e}")

                last_slot = current_slot

            time.sleep(5)


if __name__ == "__main__":
    main()
