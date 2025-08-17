import os

from worker.jobs import start_scheduler

from app import create_app

app = create_app()

if __name__ == "__main__":
    start_scheduler()
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=False,
        use_reloader=False,
    )
