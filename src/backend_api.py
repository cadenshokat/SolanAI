from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
import json
import sqlite3
from datetime import datetime, timedelta

from new_coins.new_coins import get_new_coins, get_almost_graduated_coins
from wallet_tracker.wallet_tracker import main as wallet_tracker_main
from wallet_tracker.wallet_overview import get_wallet_7d_metrics
from wallet_tracker.get_coin_data import get_coin_data  # Your function to retrieve coin data
from whale_watcher.whale import main as run_whale_watcher
from get_sol_price import update_sol_cache, get_sol_trendline, get_daychange_from_timestamp
from trend_scraper.get_trends import fetch_trending_topics
from fear_vs_greed import get_fear_vs_greed, get_fear_vs_greed_historical

app = Flask(__name__)
CORS(app)

# Global caches for coin data (for coins from solana new coins endpoints)
new_coins_cache = []
almost_coins_cache = []

# Global variable for the wallet tracker – default to an empty list.
WALLETS_TO_TRACK = []  # Updated by the user

wallet_tracker_cache = {}   # Will store keys: 'hot_buys', 'new_hot_buys', 'new_transfers'
wallet_overview_cache = {}    # Format: {wallet_address: {"7d PnL": ..., "7d Volume": ...}}
sol_price_history = {}

# --- SQLite Cache for Coin Data ---
DB_FILE = "coin_cache.db"

def init_coin_cache_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coin_cache (
            token_address TEXT PRIMARY KEY,
            coin_info TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_coin_from_cache(token):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT coin_info FROM coin_cache WHERE token_address=?", (token,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row[0])
        except Exception as e:
            print(f"Error decoding cached coin data for {token}: {e}")
            return None
    return None

def set_coin_in_cache(token, coin_info):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    data = json.dumps(coin_info)
    cursor.execute("REPLACE INTO coin_cache (token_address, coin_info) VALUES (?, ?)", (token, data))
    conn.commit()
    conn.close()

def get_all_cached_coins():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT token_address, coin_info FROM coin_cache")
    rows = cursor.fetchall()
    conn.close()
    cache = {}
    for token, info in rows:
        try:
            cache[token] = json.loads(info)
        except Exception as e:
            print(f"Error decoding cached coin data for {token}: {e}")
    return cache

# Initialize the coin cache DB on startup.
init_coin_cache_db()

def update_coin_data():
    global wallet_tracker_cache
    tokens = set()
    new_transfers = wallet_tracker_cache.get("new_transfers", {})
    for txs in new_transfers.values():
        for tx in txs:
            token = tx.get("token_address")
            if token:
                tokens.add(token)
    print("Tokens detected for coin data update:", tokens)
    for token in tokens:
        coin_info = get_coin_from_cache(token)
        if coin_info is None:
            try:
                coin_info = get_coin_data(token)
                set_coin_in_cache(token, coin_info)
                print(f"Fetched and cached data for token {token}: {coin_info}")
            except Exception as e:
                print(f"Error fetching coin data for {token}: {e}")
        else:
            print(f"Token {token} already in cache.")


def update_coin_data_loop():
    while True:
        update_coin_data()
        time.sleep(300)  # Refresh coin data every 5 minutes

# --- Existing Loops and Endpoints ---

def update_new_coins_loop():
    global new_coins_cache
    while True:
        new_coins_cache = get_new_coins()
        time.sleep(3)

def update_almost_coins_loop():
    global almost_coins_cache
    while True:
        almost_coins_cache = get_almost_graduated_coins()
        time.sleep(3)

def update_wallet_tracker_loop():
    global wallet_tracker_cache, WALLETS_TO_TRACK
    print("Starting wallet tracker loop with wallets:", WALLETS_TO_TRACK)
    while True:
        if WALLETS_TO_TRACK:
            try:
                hot_buys, new_hot_buys, new_transfers = wallet_tracker_main(WALLETS_TO_TRACK, 3)
                wallet_tracker_cache = {
                    "hot_buys": hot_buys,
                    "new_hot_buys": new_hot_buys,
                    "new_transfers": new_transfers
                }
                print("Updated wallet tracker cache:", wallet_tracker_cache)
            except Exception as e:
                print("Error in wallet tracker loop:", e)
        else:
            print("No wallets to track.")
        time.sleep(30)

def update_wallet_overview_immediate(wallets):
    global wallet_overview_cache
    for wallet in wallets:
        try:
            metrics = get_wallet_7d_metrics(wallet)
            if metrics:
                wallet_overview_cache[wallet] = metrics
            else:
                wallet_overview_cache[wallet] = {"7d PnL": "N/A", "7d Volume": "N/A"}
        except Exception as e:
            print(f"Error updating wallet overview for {wallet}: {e}")
            wallet_overview_cache[wallet] = {"7d PnL": "Error", "7d Volume": "Error"}
    print("Immediate wallet overview updated:", wallet_overview_cache)

def update_wallet_overview_loop():
    global wallet_overview_cache, WALLETS_TO_TRACK
    while True:
        if WALLETS_TO_TRACK:
            for wallet in WALLETS_TO_TRACK:
                try:
                    metrics = get_wallet_7d_metrics(wallet)
                    if metrics:
                        wallet_overview_cache[wallet] = metrics
                    else:
                        wallet_overview_cache[wallet] = {"7d PnL": "N/A", "7d Volume": "N/A"}
                except Exception as e:
                    print(f"Error in periodic wallet overview update for {wallet}: {e}")
                    wallet_overview_cache[wallet] = {"7d PnL": "Error", "7d Volume": "Error"}
            print("Periodic wallet overview updated:", wallet_overview_cache)
        else:
            print("No wallets to update for overview.")
        time.sleep(600)  # Refresh every 5 minutes

@app.route('/api/almost-graduated-coins')
def almost_coins_endpoint():
    return jsonify({"coins": almost_coins_cache})

@app.route('/api/new-coins')
def new_coins_endpoint():
    return jsonify({"coins": new_coins_cache})

@app.route('/api/wallet-tracker')
def wallet_tracker_endpoint():
    return jsonify(wallet_tracker_cache)

@app.route('/api/wallet-overview')
def wallet_overview_endpoint():
    return jsonify(wallet_overview_cache)

@app.route('/api/coin-data')
def coin_data_endpoint():
    # Return all cached coin data from SQLite.
    return jsonify(get_all_cached_coins())

@app.route('/api/sol_trendline')
def sol_trendline():
    update_sol_cache()
    trendline = get_sol_trendline()

    return trendline

db_path_trends = "trend_scraper/trending_data.db"

def get_latest_trends():
    """Retrieve the most recent trending topics record from the database."""
    conn = sqlite3.connect(db_path_trends)
    cursor = conn.cursor()
    cursor.execute("SELECT run_time, topics FROM trending ORDER BY run_time DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row  # Returns (run_time, topics_json) or None

@app.route('/api/trending')
def trending():
    latest = get_latest_trends()
    update_needed = False

    if latest:
        run_time_str, topics_json = latest
        run_time = datetime.strptime(run_time_str, '%Y-%m-%d %H:%M:%S')
        if datetime.now() - run_time > timedelta(hours=1):
            update_needed = True
    else:
        update_needed = True

    if update_needed:
        # Update the trends if no record exists or data is older than 1 hour.
        fetch_trending_topics("mrtrends454970")
        latest = get_latest_trends()
        if not latest:
            return jsonify({"error": "Failed to update trending topics"}), 500

    run_time_str, topics_json = latest
    return jsonify({
        "timestamp": run_time_str,
        "trending_topics": json.loads(topics_json)
    })

@app.route('/api/fear_vs_greed')
def fear_vs_greed():
    data = get_fear_vs_greed()

    return data

@app.route('/api/fear_vs_greed_trendline')
def fear_vs_greed_historical():
    data = get_fear_vs_greed_historical()

    return data


@app.route('/api/whale_transfers')
def whale_transfers():

    conn = sqlite3.connect('whale_watcher/whale.db')
    cursor = conn.cursor()
    cutoff_timestamp = int(time.time()) - 86400  # Last 24 hours
    cursor.execute("SELECT timestamp, transfers FROM whaleTransfers WHERE timestamp > ?", (cutoff_timestamp,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for ts, transfers_json in rows:
        try:
            transfers = json.loads(transfers_json)
        except Exception as e:
            transfers = transfers_json
        results.append({"timestamp": ts, "transfers": transfers})

    return jsonify(results)

@app.route('/api/liquidity')
def liquidity():
    ts = request.args.get("timestamp", default=0, type=int)
    conn = sqlite3.connect("liquidityAdds.db")
    cursor = conn.cursor()
    query = "SELECT timestamp, mapTransfers FROM liquidityAdds WHERE timestamp > ?"
    cursor.execute(query, (ts,))
    rows = cursor.fetchall()
    conn.close()
    data = []
    for row in rows:
        ts, map_transfers_str = row
        try:
            # Convert the stored JSON string back into a Python object
            map_transfers = json.loads(map_transfers_str)
        except json.JSONDecodeError:
            map_transfers = map_transfers_str
        data.append({"timestamp": ts, "mapTransfers": map_transfers})
    json_data = json.dumps(data)
    print(json_data)
    return json_data


def combine_events():
    events = []
    cutoff_timestamp = int(time.time()) - 180  # only consider events in the last 3 minutes

    # --- Liquidity Adds ---
    try:
        conn = sqlite3.connect("liquidityAdds.db")
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, mapTransfers FROM liquidityAdds WHERE timestamp > ?", (cutoff_timestamp,))
        rows = cursor.fetchall()
        conn.close()
        for ts, map_transfers_str in rows:
            try:
                map_transfers = json.loads(map_transfers_str)
            except Exception as e:
                print(f"Error decoding liquidity adds JSON: {e}")
                continue

            # Assuming map_transfers is either a list or a dict with a coin identifier field
            if isinstance(map_transfers, list):
                for event in map_transfers:
                    token = event.get("token_address")
                    if token:
                        events.append({
                            "timestamp": ts,
                            "token_address": token,
                            "type": "liquidity_add",
                            "details": event
                        })
            elif isinstance(map_transfers, dict):
                token = map_transfers.get("token_address")
                if token:
                    events.append({
                        "timestamp": ts,
                        "token_address": token,
                        "type": "liquidity_add",
                        "details": map_transfers
                    })
    except Exception as e:
        print("Error querying liquidity adds:", e)

    # --- Whale Transfers ---
    try:
        conn = sqlite3.connect('whale_watcher/whale.db')
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, transfers FROM whaleTransfers WHERE timestamp > ?", (cutoff_timestamp,))
        rows = cursor.fetchall()
        conn.close()
        for ts, transfers_json in rows:
            try:
                transfers = json.loads(transfers_json)
            except Exception as e:
                print(f"Error decoding whale transfers JSON: {e}")
                continue

            if isinstance(transfers, list):
                for event in transfers:
                    token = event.get("token_address")
                    if token:
                        events.append({
                            "timestamp": ts,
                            "token_address": token,
                            "type": "whale_transfer",
                            "details": event
                        })
            elif isinstance(transfers, dict):
                token = transfers.get("token_address")
                if token:
                    events.append({
                        "timestamp": ts,
                        "token_address": token,
                        "type": "whale_transfer",
                        "details": transfers
                    })
    except Exception as e:
        print("Error querying whale transfers:", e)

    # --- Wallet Purchases (from wallet_tracker_cache) ---
    # Assuming wallet purchases are stored under the keys "hot_buys" and/or "new_hot_buys" in wallet_tracker_cache.
    try:
        # Access the global wallet_tracker_cache (import or declare global in the function)
        global wallet_tracker_cache
        for key in ["hot_buys", "new_hot_buys"]:
            events_list = wallet_tracker_cache.get(key, [])
            for event in events_list:
                token = event.get("token_address")
                # Use event's timestamp if provided; otherwise, default to the current time.
                ts = event.get("timestamp", int(time.time()))
                if token:
                    events.append({
                        "timestamp": ts,
                        "token_address": token,
                        "type": key,
                        "details": event
                    })
    except Exception as e:
        print("Error accessing wallet purchases:", e)

    # --- Group events for the same token within 3 minutes ---
    # Sort events by timestamp.
    events.sort(key=lambda x: x["timestamp"])
    aggregated = {}  # key: token_address, value: list of aggregated groups
    for event in events:
        token = event["token_address"]
        ts = event["timestamp"]
        if token not in aggregated:
            aggregated[token] = []
        grouped = False
        # Check if an existing group for this token is within 3 minutes.
        for group in aggregated[token]:
            if ts - group["start_time"] <= 180:  # 3 minutes window
                group["events"].append(event)
                grouped = True
                break
        if not grouped:
            # Start a new group for this token.
            aggregated[token].append({
                "start_time": ts,
                "events": [event]
            })

    return aggregated


@app.route('/api/sol_daychange')
def sol_daychange():
    timestamp = request.args.get("timestamp")
    if not timestamp:
        return jsonify({"error": "No timestamp provided"}), 400
    dayChange = get_daychange_from_timestamp(timestamp)
    if dayChange is None:
        return jsonify({"error": "Day change not found for timestamp"}), 404
    return jsonify({"timestamp": timestamp, "dayChange": dayChange})

# Endpoint to update the list of wallets to track.
@app.route('/api/update-wallets', methods=['POST'])
def update_wallets():
    global WALLETS_TO_TRACK
    data = request.get_json()
    if not data or 'wallets' not in data:
        return jsonify({"error": "No wallets provided"}), 400

    # Only allow up to 10 wallets.
    wallets = data['wallets'][:10]
    WALLETS_TO_TRACK = wallets
    print("WALLETS_TO_TRACK updated to:", WALLETS_TO_TRACK)
    # Immediately update the wallet overview for these wallets.
    update_wallet_overview_immediate(WALLETS_TO_TRACK)
    return jsonify({"status": "Wallets updated", "wallets": WALLETS_TO_TRACK})

if __name__ == '__main__':
    # Start all update loops as daemon threads.
    thread1 = threading.Thread(target=update_new_coins_loop, daemon=True)
    thread2 = threading.Thread(target=update_almost_coins_loop, daemon=True)
    thread3 = threading.Thread(target=update_wallet_tracker_loop, daemon=True)
    thread4 = threading.Thread(target=update_wallet_overview_loop, daemon=True)
    thread5 = threading.Thread(target=update_coin_data_loop, daemon=True)
    thread6 = threading.Thread(target=run_whale_watcher, daemon=True)

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()

    app.run(debug=True, port=5000)
