from apscheduler.schedulers.background import BackgroundScheduler
from app.services import coins, wallets
from app.services import whales_ingest

def start_scheduler():
    sched = BackgroundScheduler(timezone="UTC")
    sched.add_job(coins.refresh_new_coins, "interval", seconds=30, id="new-coins", jitter=5)
    sched.add_job(coins.refresh_almost, "interval", seconds=30, id="almost-coins", jitter=5)
    sched.add_job(wallets.refresh_wallet_tracker, "interval", seconds=30, id="wallet-tracker", jitter=5)
    sched.add_job(wallets.refresh_wallet_overview, "interval", seconds=600, id="wallet-overview", jitter=30)
    sched.add_job(coins.refresh_coin_metadata, "interval", seconds=300, id="coin-meta", jitter=10)
    sched.add_job(whales_ingest.run_once, "interval", seconds=10, id="whales-ingest", jitter=3) 
    sched.start()
