import requests
import sqlite3
import json

DB_FILE = "coin_cache.db"  # Using the same DB file

def get_sol_price():
    url = "https://public-api.birdeye.so/defi/price?address=So11111111111111111111111111111111111111112"
    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": "6921317d1cdf4bbaa5df314c677190e9"
    }
    response = requests.get(url, headers=headers)
    r = response.json()
    data = r.get("data", {})

    info = {
        "price": data.get("value"),
        "timestamp": data.get("updateUnixTime"),
        "dayChange": data.get("priceChange24h")
    }
    return info

def init_sol_cache_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sol_cache (
            timestamp TEXT PRIMARY KEY,
            price TEXT,
            dayChange TEXT
        )
    """)
    conn.commit()
    conn.close()

def update_sol_cache():
    info = get_sol_price()
    if info and info["price"] and info["timestamp"] and info["dayChange"]:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            # Using REPLACE INTO to update the row if the timestamp already exists
            cursor.execute(
                "REPLACE INTO sol_cache (timestamp, price, dayChange) VALUES (?, ?, ?)",
                (str(info["timestamp"]), str(info["price"]), str(info["dayChange"]))
            )
            conn.commit()
        except Exception as e:
            print("Error updating sol cache:", e)
        finally:
            conn.close()

def get_sol_trendline():
    """
    Retrieves the stored Sol price data ordered by timestamp.
    Each record includes the timestamp, price, and dayChange.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, price, dayChange FROM sol_cache ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    conn.close()
    trend_data = [{"timestamp": row[0], "price": row[1], "dayChange": row[2]} for row in rows]
    return trend_data

def get_daychange_from_timestamp(timestamp):
    """
    Retrieves the dayChange value from the cache for a given timestamp.
    This function does not require an external API call since the data is already stored.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT dayChange FROM sol_cache WHERE timestamp=?", (timestamp,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Initialize the sol cache DB when the application starts.
init_sol_cache_db()

if __name__ == "__main__":
    update_sol_cache()
    trendline = get_sol_trendline()
    print(json.dumps(trendline, indent=2))
