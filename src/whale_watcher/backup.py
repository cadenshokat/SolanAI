import requests
import time
import json
import re

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

    if response.status_code == 200:
        return response.json().get("result", {}).get("transactions", [])
    return []

def extract_amount_from_logs(logs):
    amounts = []
    for log in logs:
        matches = re.findall(r'amount_in: (\d+)|amount_out: (\d+)', log)
        for match in matches:
            # Add non-empty matches
            amounts.extend([int(value) for value in match if value])
    return amounts


def process_whale_transactions(transactions):
    whale_transactions = {}
    for tx in transactions:
        transaction_id = tx.get("transaction", {}).get("signatures", [None])[0]
        meta = tx.get("meta", {})
        logs = meta.get("logMessages", [])
        pre_balances = meta.get("preTokenBalances", [])
        post_balances = meta.get("postTokenBalances", [])

        if meta.get("err") is None and pre_balances:

            print(transaction_id)
            print(logs)
            print("----------------------------")


def main():
    print("🚀 Starting Solana RPC Listener...")
    last_slot = get_latest_slot()

    while True:
        current_slot = get_latest_slot()

        if current_slot > last_slot:
            for slot in range(last_slot + 1, current_slot + 1):
                transactions = get_transactions_in_block(slot)
                process_whale_transactions(transactions)

            last_slot = current_slot

        time.sleep(5)

if __name__ == "__main__":
    main()
