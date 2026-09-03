from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.contract import Contract, ContractCategory, ContractStatus
from app.models.obligation import Obligation, ObligationStatus, ObligationType
from app.models.renewal import Renewal, RenewalStatus
from app.models.user import User, UserRole
from app.services.report_service import contract_summary, obligation_summary, renewal_summary, risk_summary


def make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_report_aggregations_and_risk():
    db = make_db()
    user = User(full_name="Admin", email="admin@test.local", hashed_password="x", role=UserRole.ADMINISTRATOR)
    db.add(user); db.flush()
    c = Contract(title="Service", contract_number="C-1", category=ContractCategory.SERVICE_AGREEMENT,
                 start_date=date.today(), end_date=date.today()+timedelta(days=60), status=ContractStatus.ACTIVE,
                 created_by=user.id)
    db.add(c); db.flush()
    db.add_all([
        Obligation(contract_id=c.id, title="Done", obligation_type=ObligationType.PAYMENT,
                   due_date=date.today()-timedelta(days=2), status=ObligationStatus.COMPLETED),
        Obligation(contract_id=c.id, title="Late", obligation_type=ObligationType.REPORTING,
                   due_date=date.today()-timedelta(days=2), status=ObligationStatus.PENDING),
    ])
    db.add(Renewal(contract_id=c.id, renewal_date=date.today()+timedelta(days=10),
                   previous_expiry_date=c.end_date, new_expiry_date=c.end_date+timedelta(days=365),
                   status=RenewalStatus.UPCOMING))
    db.commit()
    assert contract_summary(db)["active"] == 1
    assert obligation_summary(db)["overdue"] == 1
    assert renewal_summary(db)["upcoming"] == 1
    assert risk_summary(db)["risk_indicators"]["medium"] == 1
