import sqlite3

import requests
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
import datetime

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
    conn = sqlite3.connect('whale.db')
    cursor = conn.cursor()
    whale_transactions = {}
    for tx in transactions:

        transaction_id = tx.get("transaction", {}).get("signatures", [None])[0]
        meta = tx.get("meta", {})
        logs = meta.get("logMessages", [])
        pre_balances = meta.get("preTokenBalances", [])
        post_balances = meta.get("postTokenBalances", [])

        if meta.get("err") is None and pre_balances:
            signer = tx.get('transaction', {}).get('message', {}).get('accountKeys', [])[0]
            pre_sol = 0
            post_sol = 0
            token = ""

            for pre in pre_balances:
                if pre.get("owner") == "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                    if pre.get("mint") == "So11111111111111111111111111111111111111112":
                        pre_sol = pre.get("uiTokenAmount", {}).get("uiAmount", 0)
                    else:
                        token = pre.get("mint")

            for post in post_balances:
                if post.get("owner") == "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1":
                    if post.get("mint") == "So11111111111111111111111111111111111111112":
                        post_sol = post.get("uiTokenAmount", {}).get("uiAmount", 0)
                    else:
                        token = post.get("mint")

            difference_sol = post_sol - pre_sol

            if difference_sol < -5:
                amount = abs(difference_sol)

                info = {
                    "mint": token,
                    "amount": amount,
                    "signer": signer,
                }
                """print("Transfer Found: ")
                print(transaction_id)
                print(f"        Mint: {token}")
                print(f"        Buy Amount Sol: {amount}")"""
                whale_transactions[transaction_id] = info

    if whale_transactions:
        print(whale_transactions)
        timestamp = int(time.time())
        json_transfers = json.dumps(whale_transactions)
        cursor.execute("REPLACE INTO whaleTransfers (timestamp, transfers) VALUES (?, ?)",
                       (timestamp, json_transfers))
        conn.commit()  # Commit the transaction
        conn.close()


def main():
    #print("🚀 Starting Solana RPC Listener...")
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