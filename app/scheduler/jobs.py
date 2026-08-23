from app.database.database import SessionLocal
from app.services.obligation_service import mark_overdue_obligations


def run_overdue_scan():
    db = SessionLocal()

    try:
        updated_count = mark_overdue_obligations(db)

        print(
            f"[Scheduler] Overdue scan completed. "
            f"Updated obligations: {updated_count}"
        )

    except Exception as error:
        print(
            f"[Scheduler] Overdue scan failed: {error}"
        )

    finally:
        db.close()