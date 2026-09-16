from datetime import date, timedelta

from app.database.database import SessionLocal
from app.models.contract import Contract
from app.models.renewal import Renewal
from app.models.notification import Notification
from app.services.audit_service import create_audit_log
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


def run_renewal_reminder_scan():
    db = SessionLocal()

    try:
        today = date.today()
        reminder_date = today + timedelta(days=30)

        renewals = (
            db.query(Renewal)
            .join(Contract, Renewal.contract_id == Contract.id)
            .filter(
                Renewal.status == "upcoming",
                Renewal.renewal_date >= today,
                Renewal.renewal_date <= reminder_date,
                Contract.assigned_to.isnot(None),
            )
            .all()
        )

        created_count = 0

        for renewal in renewals:
            contract = renewal.contract

            existing_notification = (
                db.query(Notification)
                .filter(
                    Notification.user_id == contract.assigned_to,
                    Notification.contract_id == contract.id,
                    Notification.notification_type == "renewal",
                    Notification.title
                    == f"Renewal reminder: {contract.contract_number}",
                    Notification.message.contains(
                        f"renewal ID {renewal.id}"
                    ),
                )
                .first()
            )

            if existing_notification:
                continue

            notification = Notification(
                user_id=contract.assigned_to,
                contract_id=contract.id,
                title=f"Renewal reminder: {contract.contract_number}",
                message=(
                    f"Contract '{contract.contract_number}' "
                    f"is scheduled for renewal on "
                    f"{renewal.renewal_date}. "
                    f"Renewal ID: {renewal.id}."
                ),
                notification_type="renewal",
                is_read=False,
            )

            db.add(notification)
            db.flush()

            create_audit_log(
                db=db,
                user_id=contract.assigned_to,
                contract_id=contract.id,
                action="Created renewal reminder",
                entity_type="Renewal",
                entity_id=renewal.id,
                details=(
                    f"Created renewal reminder notification for "
                    f"contract '{contract.contract_number}' "
                    f"scheduled on {renewal.renewal_date}"
                ),
            )

            created_count += 1

        db.commit()

        print(
            f"[Scheduler] Renewal reminder scan completed. "
            f"Created notifications: {created_count}"
        )

    except Exception as error:
        db.rollback()

        print(
            f"[Scheduler] Renewal reminder scan failed: {error}"
        )

    finally:
        db.close()