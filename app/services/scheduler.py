from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.services.daily_monitor import check_daily_collections


def run_daily_monitor():

    db = SessionLocal()

    try:
        result = check_daily_collections(db)

        print(
            f"[Scheduler] Daily monitor executed: {result}"
        )

    finally:
        db.close()


scheduler = BackgroundScheduler()

scheduler.add_job(
    run_daily_monitor,
    trigger="cron",
    hour=20,
    minute=0,
    id="daily_collection_monitor",
    replace_existing=True
)