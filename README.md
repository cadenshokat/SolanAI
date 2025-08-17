# SolanAI (Flask + Schedulers + SQLite)

A production-style API that tracks Solana activity—new coins, wallet flows, whale buys, liquidity adds—plus SOL price trendlines, Twitter trends/sentiment, and Fear & Greed. Built with clean layering, background jobs, and a Next.js-friendly REST surface.

## Highlights
- Flask app factory + Blueprints (`/api/v1/...`)
- APScheduler background jobs (run in a separate worker)
- Centralized DB helpers (SQLite, WAL) and thin stores
- Clean “clients / services / db” layering
- Env-driven secrets (no hardcoded cookies/keys)
- Next.js SDK ready (`src/lib/api.ts` example was provided)
- pytest suite with HTTP stubs and temp DBs

---

## Stack
**Backend:** Flask, APScheduler, requests  
**Data:** SQLite (file path via env), WAL mode  
**Scraping/APIs:** twscrape, Selenium (optional), CoinGecko, Birdeye, CoinMarketCap, Solscan, Pump.fun  
**Prod serving:** Gunicorn (web) + a separate worker process
**Build**: `pyproject.toml` (setuptools)

---

## Repo Layout

```markdown
solanai/
├─ app/
│  ├─ __init__.py                  
│  ├─ api/
│  │  └─ routes.py                  
│  ├─ core/
│  │  ├─ config.py                
│  │  └─ logging.py                
│  ├─ clients/
│  │  ├─ pumpfun.py                 
│  │  ├─ solscan.py                  
│  │  └─ twscrape_pool.py           
│  ├─ db/
│  │  ├─ session.py                
│  │  ├─ coin_cache.py              
│  │  ├─ sol_store.py              
│  │  ├─ tweet_store.py             
│  │  └─ whale_store.py              
│  └─ services/
│     ├─ coin_meta.py               
│     ├─ coins.py                  
│     ├─ fear.py                   
│     ├─ market.py                   
│     ├─ wallet_metrics.py           
│     ├─ wallets.py                
│     ├─ trends.py                
│     ├─ twitter_accounts.py         
│     └─ whale_ingest.py             
├─ worker/
│  ├─ jobs.py                       
│  └─ runner.py                     
├─ cli/
│  └─ capture_twitter_cookies.py    
├─ tests/
│  ├─ conftest.py                    
│  ├─ services/
│  │  ├─ test_coin_meta.py
│  │  ├─ test_coins.py
│  │  ├─ test_fear.py
│  │  ├─ test_market.py
│  │  ├─ test_trends.py
│  │  ├─ test_twitter_accounts.py
│  │  ├─ test_wallet_metrics.py
│  │  ├─ test_wallets.py
│  │  └─ test_whale_ingest.py
│  └─ api/
│     └─ test_routes.py             
├─ .env.example                     
├─ .dockerignore
├─ Dockerfile
├─ docker-compose.yml
├─ Makefile
├─ pyproject.toml                 
├─ README.md
└─ run.py                           
```

---

## Quickstart (Local)

### 1. Python & deps
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install .
# editable + dev tools (tests, coverage)
pip install -e .[dev]
```

### 2. Configure env

Copy and fill in ```.env``` (see example below):

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

**Twitter accounts JSON schema (if you use ```TW_ACCOUNTS_FILE```):**
```json
{
  "mrtrends454970": {
    "password": "******",
    "email": "name@example.com",
    "email_password": "******",
    "cookies": "cookies_mrtrends454970.json"
  }
}
```
- Store cookies under ```tweet_scraper/cookies/``` (do not commit them).

### 3) Run (local dev)

```bash
# API (Flask app)
make run
# Scheduler worker (APScheduler jobs)
make run-worker
```
API will be at ```http://localhost:5000/api/v1```.

## Docker

```bash
# Build and run API + worker
docker compose up --build -d

# Logs
docker compose logs -f --tail=200 api worker

# Smoke test
curl http://localhost:5000/api/v1/health
```
Selenium inside Docker uses chromium + chromium-driver already installed (see Dockerfile). Ensure ```CHROMEDRIVER_PATH=/usr/bin/chromedriver``` and mount ```tweet_scraper/cookies``` if you keep cookies outside the image.

## API Endpoints (summary)

```bash
GET  /api/v1/health
GET  /api/v1/ready

# Coins
GET  /api/v1/coins/new
GET  /api/v1/coins/almost
GET  /api/v1/coins/cache

# Wallets
GET  /api/v1/wallets/tracker
GET  /api/v1/wallets/overview
POST /api/v1/wallets/update            { "wallets": ["addr1", ...] }  # max 10

# SOL market
GET  /api/v1/sol/trendline
GET  /api/v1/sol/daychange?timestamp=<epoch-seconds>

# Twitter Trends
GET  /api/v1/trending

# Fear & Greed
GET  /api/v1/fear-vs-greed
GET  /api/v1/fear-vs-greed/history

# Whales / Liquidity
GET  /api/v1/whales/transfers?last_seconds=86400
GET  /api/v1/liquidity?timestamp=0
```

### Background Jobs (APScheduler)

```worker/jobs.py``` registers recurring tasks:
- ```coins.refresh_new_coins``` — every 30s
- ```coins.refresh_almost``` — every 30s
- ```wallets.refresh_wallet_tracker``` — every 30s
- ```wallets.refresh_wallet_overview``` — every 10m
- ```coins.refresh_coin_metadata``` — every 5m
- ```whales_ingest.run_once``` — every 10s (poll Solana RPC blocks)

In Docker, these run in the worker container (```python -m worker.runner```).

## Testing

```bash
# run tests
pytest

# coverage (HTML report)
pytest --cov=app --cov=worker --cov-report=html
```
- Tests use temp SQLite DBs (no real files touched). 
- External HTTP calls are stubbed (responses). 
- Selenium is mocked. 
- Async twscrape logic is simulated with fakes. 
- Config: see ```pytest.ini``` and ```.coveragerc```.

### Next.js Integration

Use the earlier ```src/lib/api.ts``` helper or fetch directly:

```ts
const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:5000/api/v1";

const res = await fetch(`${BASE}/coins/new`, { cache: "no-store" });
const data = await res.json();
```
Set ```NEXT_PUBLIC_API_BASE``` in your Next.js ```.env.local```.

## Security & Ops Notes
- **Never commit secrets or cookies**. Use ```.env```, Docker secrets, or your platform’s secret manager. 
- SQLite files should live under a mounted volume in production. 
- Twitter scraping requires valid cookies/accounts and may be rate-limited; keep pools small and back off on errors.

## License
MIT