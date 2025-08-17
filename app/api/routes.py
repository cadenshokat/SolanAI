from __future__ import annotations

from typing import Any, Dict

from flask import Blueprint, jsonify, request

# NEW
from ..services import coins, fear, market, trends, wallets, whales

api = Blueprint("api", __name__)

# ---------
# Coins
# ---------


@api.get("/coins/new")
def new_coins() -> Any:
    """List newest Pump.fun coins (cached in memory by scheduler)."""
    return jsonify({"coins": coins.get_new()})


@api.get("/coins/almost")
def almost_coins() -> Any:
    """List 'about to graduate' coins (cached in memory by scheduler)."""
    return jsonify({"coins": coins.get_almost()})


@api.get("/coins/cache")
def coin_cache_all() -> Any:
    """All token metadata we’ve fetched & cached (via coin_meta + SQLite)."""
    return jsonify(coins.get_cached_coins())


# ---------
# Wallets
# ---------


@api.get("/wallets/tracker")
def wallet_tracker() -> Any:
    """
    Hot buys, new hot buys, and recent transfers seen across tracked wallets.
    Populated by the background job calling wallets.refresh_wallet_tracker().
    """
    return jsonify(wallets.get_tracker_cache())


@api.get("/wallets/overview")
def wallet_overview() -> Any:
    """7d PnL and Volume per tracked wallet (scraped via Selenium)."""
    return jsonify(wallets.get_overview_cache())


@api.post("/wallets/update")
def update_wallets() -> Any:
    """
    Update the set of wallets to track.
    Body: {"wallets": ["<addr1>", "<addr2>", ...]}   (max 10)
    """
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    wl = data.get("wallets")
    if not isinstance(wl, list):
        return jsonify({"error": "Field 'wallets' (array) is required"}), 400

    # Normalize & limit to 10
    wallets_list = [str(w).strip() for w in wl if isinstance(w, (str, bytes))][:10]
    updated = wallets.update_wallets(wallets_list)
    return jsonify({"status": "ok", "wallets": updated})


# ---------
# Solana price/trend
# ---------


@api.get("/sol/trendline")
def sol_trendline():
    market.refresh_sol_price()
    return jsonify(market.get_sol_trendline())


@api.get("/sol/daychange")
def sol_daychange():
    ts = request.args.get("timestamp", type=int)
    if ts is None:
        return jsonify({"error": "query param 'timestamp' (int) is required"}), 400
    dc = market.get_daychange_from_timestamp(ts)
    if dc is None:
        return jsonify({"error": "day change not found for timestamp"}), 404
    return jsonify({"timestamp": ts, "dayChange": dc})


# -----------------------------------------------------------------------------
# Trends (Twitter)
# -----------------------------------------------------------------------------


@api.get("/trending")
def trending() -> Any:
    """
    Returns the latest trending topics from trends DB.
    If the last run is older than 1 hour, triggers a refresh (sync).
    """
    if trends.needs_update(1):
        trends.refresh_trends()
    return jsonify(trends.get_trending())


# ---------
# Fear vs Greed
# ---------


@api.get("/fear-vs-greed")
def fear_vs_greed_current() -> Any:
    """Current fear vs greed data."""
    return jsonify(fear.current())


@api.get("/fear-vs-greed/history")
def fear_vs_greed_history() -> Any:
    """Historical fear vs greed trendline."""
    return jsonify(fear.history())


# ---------
# Whales / Liquidity
# ---------


@api.get("/whales/transfers")
def whale_transfers() -> Any:
    """
    Whale transfers recorded in the last 24h (default).
    Optionally override window via ?last_seconds=<int>
    """
    last_seconds = request.args.get("last_seconds", default=86400, type=int)
    return jsonify(whales.whale_transfers(last_seconds=last_seconds))


@api.get("/liquidity")
def liquidity() -> Any:
    """
    Liquidity adds since the given timestamp.
    ?timestamp=<epoch-seconds>  (defaults to 0)
    """
    ts = request.args.get("timestamp", default=0, type=int)
    return jsonify(whales.liquidity_since(ts))


# ---------
# Health
# ---------


@api.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"})


@api.get("/ready")
def ready() -> Any:
    return jsonify({"status": "ok"})
