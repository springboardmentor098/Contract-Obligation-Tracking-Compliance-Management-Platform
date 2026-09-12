from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.models.user import User
from app.services.report_service import dashboard_summary, report_rows, risk_summary


def test_dashboard_summary_and_risk_use_current_records():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    user = User(
        full_name="Report User",
        email="report@example.com",
        role="Administrator",
        password_hash="not-a-real-password",
    )
    session.add(user)
    session.flush()
    contract = Contract(
        title="Vendor Agreement",
        contract_number="CNT-REPORT-1",
        category="Vendor",
        status="Active",
        created_by=user.id,
        end_date=date.today() + timedelta(days=10),
    )
    session.add(contract)
    session.flush()
    session.add_all([
        Obligation(
            contract_id=contract.id,
            title="Late filing",
            obligation_type="Reporting Requirement",
            due_date=date.today() - timedelta(days=1),
            status="Overdue",
            assigned_to=user.id,
        ),
        Obligation(
            contract_id=contract.id,
            title="Late payment",
            obligation_type="Payment Obligation",
            due_date=date.today() - timedelta(days=2),
            status="Overdue",
            assigned_to=user.id,
        ),
        Obligation(
            contract_id=contract.id,
            title="Completed filing",
            obligation_type="Reporting Requirement",
            due_date=date.today(),
            status="Completed",
            assigned_to=user.id,
            completion_date=date.today(),
        ),
    ])
    session.add(Renewal(
        contract_id=contract.id,
        renewal_date=date.today() + timedelta(days=30),
        previous_expiry_date=contract.end_date,
        status="Upcoming",
        assigned_to=user.id,
    ))
    session.commit()

    summary = dashboard_summary(session)

    assert summary["contracts"]["active"] == 1
    assert summary["obligations"]["total"] == 3
    assert summary["obligations"]["overdue"] == 2
    assert summary["renewals"]["approaching_expiry"][0]["contract_number"] == "CNT-REPORT-1"
    assert summary["compliance"]["non_compliant"] == 1
    assert risk_summary(session)[0]["overdue_obligations"] == 2
    assert len(report_rows(session, "obligations")) == 3
    assert len(report_rows(session, "renewals")) == 1
    assert len(report_rows(session, "contracts")) == 1
    assert len(report_rows(session, "compliance")) == 1

    session.close()