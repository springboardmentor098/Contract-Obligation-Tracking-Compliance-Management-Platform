import random
from datetime import date, datetime, timedelta
from app.database.database import SessionLocal
from app.core.roles import UserRole, normalize_role
from app.core.security import get_password_hash
from app.models import (
    User, Contract, ContractVersion, Obligation, Renewal,
    Notification, Report, AuditLog, Activity
)

ROLES = [
    UserRole.ADMINISTRATOR.value,
    UserRole.LEGAL_MANAGER.value,
    UserRole.COMPLIANCE_OFFICER.value,
    UserRole.CONTRACT_MANAGER.value,
    UserRole.DEPARTMENT_HEAD.value,
    UserRole.EMPLOYEE.value,
]

DEPARTMENTS = ["Legal", "Compliance", "Finance", "Operations", "Sales", "Engineering", "HR"]
CONTRACT_TYPES = ["Service", "Software", "NDA", "Vendor", "Employment", "Licensing", "Procurement"]
CONTRACT_STATUSES = ["Active", "Pending Review", "Under Negotiation", "Expired", "Terminated"]
OBLIGATION_TYPES = ["Compliance", "Financial", "Audit", "Security", "Delivery", "Reporting"]
PRIORITIES = ["High", "Medium", "Low", "Urgent"]
RENEWAL_TYPES = ["Automatic", "Manual", "Optional"]
RENEWAL_STATUSES = ["Upcoming", "Pending Notice", "Renewed", "Not Started", "Expired"]
NOTIFICATION_TYPES = ["Reminder", "Urgent", "Info", "Status Update", "Warning"]
REPORT_TYPES = ["Compliance", "Financial", "Renewal", "Audit", "Risk Analysis"]
ACTIONS = ["CREATE", "UPDATE", "DELETE", "UPLOAD", "LOGIN"]
ACTIVITY_TYPES = ["Contract Created", "Obligation Assigned", "Version Uploaded", "NDA Activated", "Status Change", "Report Generated"]


def seed_database():
    db = SessionLocal()
    try:
        print("Starting ContractIQ Database Seeding (Target: ~50 records per table)...")

        # 1. Update/Normalize existing users
        existing_users = db.query(User).all()
        for u in existing_users:
            old_role = u.role
            u.role = normalize_role(old_role)
            if u.user_id == 1 or u.email.lower() == "rathna@ex.com" or "admin" in u.email.lower():
                u.role = UserRole.ADMINISTRATOR.value
            if not getattr(u, "password_hash", None):
                u.password_hash = get_password_hash("password123")
        db.commit()

        # 2. Seed Users to 50
        current_user_count = db.query(User).count()
        if current_user_count < 50:
            default_pw = get_password_hash("password123")
            new_users = []
            for i in range(current_user_count + 1, 51):
                role = ROLES[(i - 1) % len(ROLES)]
                dept = DEPARTMENTS[(i - 1) % len(DEPARTMENTS)]
                new_users.append(User(
                    user_id=i,
                    name=f"User {i} ({role.split()[0]})",
                    email=f"user{i}@contractiq.com",
                    password_hash=default_pw,
                    role=role,
                    department=dept,
                    is_active=True
                ))
            db.add_all(new_users)
            db.commit()
        print(f"Users table count: {db.query(User).count()}")

        all_users = db.query(User).all()
        user_ids = [u.user_id for u in all_users]

        # 3. Seed Contracts to 50
        current_contract_count = db.query(Contract).count()
        if current_contract_count < 50:
            new_contracts = []
            for i in range(current_contract_count + 1, 51):
                ctype = CONTRACT_TYPES[(i - 1) % len(CONTRACT_TYPES)]
                cstatus = CONTRACT_STATUSES[(i - 1) % len(CONTRACT_STATUSES)]
                owner = user_ids[(i - 1) % len(user_ids)]
                creator = user_ids[i % len(user_ids)]
                s_date = date(2025, 1, 1) + timedelta(days=i * 5)
                e_date = s_date + timedelta(days=365)
                val = round(10000.00 + (i * 2500.50), 2)
                
                new_contracts.append(Contract(
                    contract_id=i,
                    title=f"{ctype} Contract #{i} - Partner {i}",
                    contract_type=ctype,
                    counterparty_name=f"Partner Corp {i}",
                    status=cstatus,
                    start_date=s_date,
                    end_date=e_date,
                    contract_value=val,
                    owner_id=owner,
                    created_by=creator
                ))
            db.add_all(new_contracts)
            db.commit()
        print(f"Contracts table count: {db.query(Contract).count()}")

        all_contracts = db.query(Contract).all()
        contract_ids = [c.contract_id for c in all_contracts]

        # 4. Seed Contract Versions to 50
        current_version_count = db.query(ContractVersion).count()
        if current_version_count < 50:
            new_versions = []
            for i in range(current_version_count + 1, 51):
                cid = contract_ids[(i - 1) % len(contract_ids)]
                uploader = user_ids[(i - 1) % len(user_ids)]
                new_versions.append(ContractVersion(
                    version_id=i,
                    contract_id=cid,
                    version_number=(i % 3) + 1,
                    file_url=f"https://storage.contractiq.com/docs/contract_{cid}_v{i}.pdf",
                    summary=f"Version {i} document update with revised legal clauses.",
                    uploaded_by=uploader,
                    is_current=True
                ))
            db.add_all(new_versions)
            db.commit()
        print(f"ContractVersions table count: {db.query(ContractVersion).count()}")

        all_versions = db.query(ContractVersion).all()

        # Update current_version_id on contracts
        for c in all_contracts:
            v_match = [v for v in all_versions if v.contract_id == c.contract_id]
            if v_match:
                c.current_version_id = v_match[-1].version_id
        db.commit()

        # 5. Seed Obligations to 50
        current_ob_count = db.query(Obligation).count()
        if current_ob_count < 50:
            new_obs = []
            for i in range(current_ob_count + 1, 51):
                cid = contract_ids[(i - 1) % len(contract_ids)]
                resp_user = user_ids[(i - 1) % len(user_ids)]
                otype = OBLIGATION_TYPES[(i - 1) % len(OBLIGATION_TYPES)]
                prio = PRIORITIES[(i - 1) % len(PRIORITIES)]
                due = date(2025, 9, 1) + timedelta(days=i * 3)

                new_obs.append(Obligation(
                    obligation_id=i,
                    contract_id=cid,
                    title=f"Obligation #{i}: {otype} Deliverable for Contract #{cid}",
                    description=f"Detailed execution terms for obligation requirement #{i}.",
                    obligation_type=otype,
                    due_date=due,
                    responsible_user_id=resp_user,
                    status="Pending" if i % 2 == 0 else "Completed",
                    priority=prio
                ))
            db.add_all(new_obs)
            db.commit()
        print(f"Obligations table count: {db.query(Obligation).count()}")

        all_obligations = db.query(Obligation).all()
        obligation_ids = [o.obligation_id for o in all_obligations]

        # 6. Seed Renewals to 50
        current_rn_count = db.query(Renewal).count()
        if current_rn_count < 50:
            new_rns = []
            for i in range(current_rn_count + 1, 51):
                cid = contract_ids[(i - 1) % len(contract_ids)]
                rtype = RENEWAL_TYPES[(i - 1) % len(RENEWAL_TYPES)]
                rstatus = RENEWAL_STATUSES[(i - 1) % len(RENEWAL_STATUSES)]
                rdate = date(2026, 1, 1) + timedelta(days=i * 6)
                new_end = rdate + timedelta(days=365)

                new_rns.append(Renewal(
                    renewal_id=i,
                    contract_id=cid,
                    renewal_type=rtype,
                    notice_period_days=30 + (i % 4) * 15,
                    renewal_date=rdate,
                    new_end_date=new_end,
                    status=rstatus,
                    reminder_sent=(i % 2 == 0)
                ))
            db.add_all(new_rns)
            db.commit()
        print(f"Renewals table count: {db.query(Renewal).count()}")

        # 7. Seed Notifications to 50
        current_nt_count = db.query(Notification).count()
        if current_nt_count < 50:
            new_nts = []
            for i in range(current_nt_count + 1, 51):
                uid = user_ids[(i - 1) % len(user_ids)]
                cid = contract_ids[(i - 1) % len(contract_ids)]
                oid = obligation_ids[(i - 1) % len(obligation_ids)]
                ntype = NOTIFICATION_TYPES[(i - 1) % len(NOTIFICATION_TYPES)]

                new_nts.append(Notification(
                    notification_id=i,
                    user_id=uid,
                    related_contract_id=cid,
                    related_obligation_id=oid,
                    type=ntype,
                    message=f"Notification alert #{i}: Action required for Contract #{cid}.",
                    is_read=(i % 3 == 0)
                ))
            db.add_all(new_nts)
            db.commit()
        print(f"Notifications table count: {db.query(Notification).count()}")

        # 8. Seed Reports to 50
        current_rp_count = db.query(Report).count()
        if current_rp_count < 50:
            new_rps = []
            for i in range(current_rp_count + 1, 51):
                uid = user_ids[(i - 1) % len(user_ids)]
                rtype = REPORT_TYPES[(i - 1) % len(REPORT_TYPES)]

                new_rps.append(Report(
                    report_id=i,
                    report_name=f"{rtype} Summary Report #{i}",
                    report_type=rtype,
                    generated_by=uid,
                    filters_json={"status": "Active", "batch": i},
                    file_url=f"https://storage.contractiq.com/reports/report_{i}.pdf"
                ))
            db.add_all(new_rps)
            db.commit()
        print(f"Reports table count: {db.query(Report).count()}")

        # 9. Seed Audit Logs to 50
        current_al_count = db.query(AuditLog).count()
        if current_al_count < 50:
            new_als = []
            for i in range(current_al_count + 1, 51):
                uid = user_ids[(i - 1) % len(user_ids)]
                act = ACTIONS[(i - 1) % len(ACTIONS)]

                new_als.append(AuditLog(
                    log_id=i,
                    user_id=uid,
                    entity_type="Contract" if i % 2 == 0 else "Obligation",
                    entity_id=i,
                    action=act,
                    old_value={"version": 1},
                    new_value={"version": 2, "updated_by": uid},
                    ip_address=f"192.168.1.{(i % 50) + 1}"
                ))
            db.add_all(new_als)
            db.commit()
        print(f"AuditLogs table count: {db.query(AuditLog).count()}")

        # 10. Seed Activities to 50
        current_act_count = db.query(Activity).count()
        if current_act_count < 50:
            new_acts = []
            for i in range(current_act_count + 1, 51):
                uid = user_ids[(i - 1) % len(user_ids)]
                cid = contract_ids[(i - 1) % len(contract_ids)]
                atype = ACTIVITY_TYPES[(i - 1) % len(ACTIVITY_TYPES)]

                new_acts.append(Activity(
                    activity_id=i,
                    user_id=uid,
                    contract_id=cid,
                    activity_type=atype,
                    description=f"Activity #{i}: Executed {atype} operation for Contract #{cid}."
                ))
            db.add_all(new_acts)
            db.commit()
        print(f"Activities table count: {db.query(Activity).count()}")

        print("\n==================================================")
        print("[SUCCESS] DATABASE SEEDING COMPLETED: ALL 9 TABLES HAVE 50 RECORDS!")
        print("==================================================")

    except Exception as e:
        db.rollback()
        print("Error during database seeding:", e)
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
