# SolanAI (Flask + Schedulers + SQLite)

A small, production-style API that tracks Solana activity (new coins, wallet flows, whale buys, liquidity adds), SOL price trendlines, Twitter trends/sentiment, and Fear & Greed — with clean layering, background jobs, and a Next.js-friendly REST surface.

## Highlights
- Flask app factory + Blueprints (`/api/v1/...`)
- Background jobs via APScheduler (separate worker-friendly)
- Centralized DB helpers (SQLite, WAL) and thin stores
- Clean “clients / services / db” layering
- Env-driven secrets (no hardcoded cookies/keys)
- Next.js SDK ready (`src/lib/api.ts` example was provided)

---

## Stack
**Backend:** Flask, APScheduler, requests  
**Data:** SQLite (file path via env), WAL mode  
**Scraping/APIs:** twscrape, Selenium (optional), CoinGecko, Birdeye, CoinMarketCap, Solscan, Pump.fun  
**Prod serving:** Gunicorn (web) + a separate worker process

---

## Repo Layout
```
solwatch/
app/
init.py
api/routes.py
core/{config.py, logging.py}
clients/{solscan.py, pumpfun.py, twscrape_pool.py}
db/{session.py, coin_cache.py, sol_store.py, tweet_store.py, whale_store.py}
services/{coins.py, coin_meta.py, wallet_metrics.py, wallets.py,
whales.py, whales_ingest.py, trends.py, tweets.py, twitter_accounts.py,
fear.py, market.py}
cli/capture_twitter_cookies.py
worker/jobs.py
run.py
requirements.txt
.env.example
Dockerfile
docker-compose.yml
Makefile
.gitignore
README.md
```

---

## Quickstart (Local)

### 1. Python & deps
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure env

Copy and fill in ```.env```:

```env
# API
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=5000
CORS_ORIGINS=["http://localhost:3000"]

# DBs
DB_PATH=data/main.db
LIQUIDITY_DB=liquidityAdds.db
TRENDS_DB=trend_scraper/trending_data.db

# Pump.fun
PUMPFUN_UA=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36
PUMPFUN_REFERER=https://pump.fun/

# Solscan
SOLSCAN_COOKIE=
SOLSCAN_AUTH=

# Coin metadata
COINGECKO_API_KEY=

# SOL price (Birdeye)
BIRDEYE_API_KEY=
SOL_MINT=So11111111111111111111111111111111111111112

# Fear & Greed (CoinMarketCap)
CMC_API_KEY=

# Twitter / Trends
TW_ACCOUNTS_PY=config.twitter_accounts
# TW_ACCOUNTS_FILE=config/twitter_accounts.json
TW_COOKIES_DIR=tweet_scraper/cookies
CHROMEDRIVER_PATH=/usr/bin/chromedriver
TRENDS_USER=twitterUser
```