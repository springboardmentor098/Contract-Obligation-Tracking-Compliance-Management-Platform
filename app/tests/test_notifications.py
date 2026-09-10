from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.user import User
from app.services.notification_service import (
    create_notification,
    generate_compliance_alert,
    generate_obligation_due_alerts,
    generate_overdue_alerts,
    generate_renewal_reminders,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)


def test_notification_lifecycle_and_proactive_generators(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    user = User(
        full_name="Notification User",
        email="notify@example.com",
        role="Compliance Officer",
        password_hash="test",
    )
    session.add(user)
    session.flush()
    contract = Contract(
        title="Expiring Agreement",
        contract_number="CNT-NOTIFY-1",
        category="Vendor",
        status="Active",
        created_by=user.id,
        assigned_to=user.id,
        end_date=date.today() + timedelta(days=30),
    )
    session.add(contract)
    session.flush()
    session.add_all([
        Obligation(
            contract_id=contract.id,
            title="Due soon",
            obligation_type="Reporting Requirement",
            due_date=date.today() + timedelta(days=3),
            status="Pending",
            assigned_to=user.id,
        ),
        Obligation(
            contract_id=contract.id,
            title="Overdue item",
            obligation_type="Payment Obligation",
            due_date=date.today() - timedelta(days=1),
            status="Pending",
            assigned_to=user.id,
        ),
    ])
    session.commit()

    assert len(generate_renewal_reminders(session)) == 1
    assert len(generate_obligation_due_alerts(session)) == 1
    assert len(generate_overdue_alerts(session)) == 1
    assert len(generate_overdue_alerts(session)) == 0
    assert len(generate_compliance_alert(session, contract.id, "Non-Compliant", "High", 1)) == 1

    notification = create_notification(
        session,
        user.id,
        "Contract Status Alert",
        "Status changed",
        "The contract status changed.",
    )
    assert notification.status == "Unread"
    mark_notification_as_read(session, notification)
    assert notification.status == "Read"
    assert notification.read_at is not None
    assert mark_all_notifications_as_read(session, user.id) == 4
    assert all(item.status == "Read" for item in user.notifications)
    session.close()