from datetime import date, datetime

from sqlalchemy import select

from app.database.database import SessionLocal
from app.models import (
    Activity,
    AuditLog,
    Contract,
    ContractVersion,
    Notification,
    Obligation,
    Renewal,
    Report,
    User,
)


def seed_database():
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. USERS
        # ---------------------------------------------------------
        users = [
            User(
                full_name="ContractIQ Admin",
                email="seed.admin@contractiq.com",
                password="SeedPassword123",
                role="Admin",
                is_active=True,
            ),
            User(
                full_name="Contract Manager",
                email="seed.manager@contractiq.com",
                password="SeedPassword123",
                role="Manager",
                is_active=True,
            ),
            User(
                full_name="Compliance Officer",
                email="seed.compliance@contractiq.com",
                password="SeedPassword123",
                role="Compliance Officer",
                is_active=True,
            ),
        ]

        for user in users:
            existing_user = db.scalar(
                select(User).where(User.email == user.email)
            )

            if existing_user is None:
                db.add(user)

        db.flush()

        # Get the actual users from the database
        admin = db.scalar(
            select(User).where(User.email == "seed.admin@contractiq.com")
        )

        manager = db.scalar(
            select(User).where(User.email == "seed.manager@contractiq.com")
        )

        compliance = db.scalar(
            select(User).where(
                User.email == "seed.compliance@contractiq.com"
            )
        )

        # ---------------------------------------------------------
        # 2. CONTRACTS
        # ---------------------------------------------------------
        contracts = [
            Contract(
                title="Software Development Agreement",
                contract_number="CON-2026-001",
                category="Technology",
                status="Active",
                start_date=date(2026, 1, 10),
                end_date=date(2027, 1, 9),
                created_by=admin.id,
                assigned_to=manager.id,
            ),
            Contract(
                title="Cloud Services Agreement",
                contract_number="CON-2026-002",
                category="Cloud Services",
                status="Active",
                start_date=date(2026, 3, 1),
                end_date=date(2027, 2, 28),
                created_by=manager.id,
                assigned_to=compliance.id,
            ),
            Contract(
                title="Vendor Service Agreement",
                contract_number="CON-2026-003",
                category="Vendor",
                status="Under Review",
                start_date=date(2026, 5, 15),
                end_date=date(2027, 5, 14),
                created_by=compliance.id,
                assigned_to=manager.id,
            ),
        ]

        for contract in contracts:
            existing_contract = db.scalar(
                select(Contract).where(
                    Contract.contract_number == contract.contract_number
                )
            )

            if existing_contract is None:
                db.add(contract)

        db.flush()

        contract1 = db.scalar(
            select(Contract).where(
                Contract.contract_number == "CON-2026-001"
            )
        )

        contract2 = db.scalar(
            select(Contract).where(
                Contract.contract_number == "CON-2026-002"
            )
        )

        contract3 = db.scalar(
            select(Contract).where(
                Contract.contract_number == "CON-2026-003"
            )
        )

        # ---------------------------------------------------------
        # 3. CONTRACT VERSIONS
        # ---------------------------------------------------------
        versions = [
            ContractVersion(
                contract_id=contract1.id,
                version_number=1,
                document_path="/documents/contracts/CON-2026-001-v1.pdf",
                created_by=admin.id,
                created_at=datetime(2026, 1, 10, 10, 30),
            ),
            ContractVersion(
                contract_id=contract1.id,
                version_number=2,
                document_path="/documents/contracts/CON-2026-001-v2.pdf",
                created_by=manager.id,
                created_at=datetime(2026, 2, 5, 14, 15),
            ),
            ContractVersion(
                contract_id=contract2.id,
                version_number=1,
                document_path="/documents/contracts/CON-2026-002-v1.pdf",
                created_by=manager.id,
                created_at=datetime(2026, 3, 1, 9, 45),
            ),
        ]

        for version in versions:
            existing_version = db.scalar(
                select(ContractVersion).where(
                    ContractVersion.contract_id == version.contract_id,
                    ContractVersion.version_number == version.version_number,
                )
            )

            if existing_version is None:
                db.add(version)

        db.flush()

        # ---------------------------------------------------------
        # 4. OBLIGATIONS
        # ---------------------------------------------------------
        obligations = [
            Obligation(
                contract_id=contract1.id,
                title="Submit Monthly Compliance Report",
                description="Submit the required monthly compliance report.",
                obligation_type="Reporting",
                due_date=date(2026, 9, 5),
                assigned_to=manager.id,
                status="Pending",
                progress=40,
            ),
            Obligation(
                contract_id=contract2.id,
                title="Review Security Requirements",
                description="Review and confirm all cloud security requirements.",
                obligation_type="Security",
                due_date=date(2026, 9, 15),
                assigned_to=compliance.id,
                status="In Progress",
                progress=70,
            ),
            Obligation(
                contract_id=contract3.id,
                title="Vendor Performance Review",
                description="Complete the quarterly vendor performance review.",
                obligation_type="Review",
                due_date=date(2026, 10, 1),
                assigned_to=manager.id,
                status="Pending",
                progress=20,
            ),
        ]

        for obligation in obligations:
            db.add(obligation)

        db.flush()

        # ---------------------------------------------------------
        # 5. RENEWALS
        # ---------------------------------------------------------
        renewals = [
            Renewal(
                contract_id=contract1.id,
                renewal_date=date(2026, 12, 10),
                status="Upcoming",
                approval_status="Pending",
                notes="Renewal review required before the contract end date.",
            ),
            Renewal(
                contract_id=contract2.id,
                renewal_date=date(2027, 1, 15),
                status="Planned",
                approval_status="Approved",
                notes="Renewal approved subject to final documentation.",
            ),
        ]

        for renewal in renewals:
            db.add(renewal)

        db.flush()

        # ---------------------------------------------------------
        # 6. NOTIFICATIONS
        # ---------------------------------------------------------
        notifications = [
            Notification(
                user_id=admin.id,
                notification_type="Contract",
                message="Contract CON-2026-001 requires attention.",
                channel="Email",
                is_read=False,
                created_at=datetime(2026, 8, 10, 9, 0),
            ),
            Notification(
                user_id=manager.id,
                notification_type="Obligation",
                message="An obligation is approaching its due date.",
                channel="In-App",
                is_read=False,
                created_at=datetime(2026, 8, 11, 10, 30),
            ),
            Notification(
                user_id=compliance.id,
                notification_type="Renewal",
                message="Cloud Services Agreement renewal is upcoming.",
                channel="Email",
                is_read=True,
                created_at=datetime(2026, 8, 12, 11, 15),
            ),
        ]

        for notification in notifications:
            db.add(notification)

        db.flush()

        # ---------------------------------------------------------
        # 7. REPORTS
        # ---------------------------------------------------------
        reports = [
            Report(
                report_type="Contract Summary",
                generated_by=admin.id,
                file_format="PDF",
                file_path="/reports/contract-summary-2026-08.pdf",
                created_at=datetime(2026, 8, 10, 15, 0),
            ),
            Report(
                report_type="Compliance Report",
                generated_by=compliance.id,
                file_format="PDF",
                file_path="/reports/compliance-report-2026-08.pdf",
                created_at=datetime(2026, 8, 12, 16, 30),
            ),
        ]

        for report in reports:
            db.add(report)

        db.flush()

        # ---------------------------------------------------------
        # 8. AUDIT LOGS
        # ---------------------------------------------------------
        audit_logs = [
            AuditLog(
                user_id=admin.id,
                action="CREATE",
                entity_type="Contract",
                details="Created contract CON-2026-001.",
                created_at=datetime(2026, 8, 10, 9, 30),
            ),
            AuditLog(
                user_id=manager.id,
                action="UPDATE",
                entity_type="Obligation",
                details="Updated progress for compliance obligation.",
                created_at=datetime(2026, 8, 11, 13, 20),
            ),
            AuditLog(
                user_id=compliance.id,
                action="REVIEW",
                entity_type="Contract",
                details="Reviewed contract CON-2026-002.",
                created_at=datetime(2026, 8, 12, 14, 10),
            ),
        ]

        for audit_log in audit_logs:
            db.add(audit_log)

        db.flush()

        # ---------------------------------------------------------
        # 9. ACTIVITIES
        # ---------------------------------------------------------
        activities = [
            Activity(
                user_id=admin.id,
                activity_type="Contract Created",
                description="Created a new software development contract.",
                created_at=datetime(2026, 8, 10, 9, 35),
            ),
            Activity(
                user_id=manager.id,
                activity_type="Obligation Updated",
                description="Updated the progress of a contract obligation.",
                created_at=datetime(2026, 8, 11, 13, 25),
            ),
            Activity(
                user_id=compliance.id,
                activity_type="Contract Reviewed",
                description="Reviewed the cloud services contract.",
                created_at=datetime(2026, 8, 12, 14, 15),
            ),
        ]

        for activity in activities:
            db.add(activity)

        db.commit()

        print("Database seed completed successfully.")
        print("3 users")
        print("3 contracts")
        print("3 contract versions")
        print("3 obligations")
        print("2 renewals")
        print("3 notifications")
        print("2 reports")
        print("3 audit logs")
        print("3 activities")

    except Exception as e:
        db.rollback()
        print("Database seed failed.")
        print(f"Error: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()