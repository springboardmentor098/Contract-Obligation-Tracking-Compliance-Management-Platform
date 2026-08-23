from apscheduler.schedulers.background import BackgroundScheduler

from app.scheduler.jobs import run_overdue_scan


scheduler = BackgroundScheduler()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            run_overdue_scan,
            "interval",
            hours=24,
            id="overdue_obligation_scan",
            replace_existing=True,
        )

        scheduler.start()

        print("[Scheduler] Started successfully.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

        print("[Scheduler] Stopped successfully.")