from datetime import date, datetime, timedelta

from app.database.database import SessionLocal
from app.core.security import hash_password

from app.models.user import User
from app.models.contract import Contract
from app.models.contract_version import ContractVersion
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.models.notification import Notification
from app.models.report import Report
from app.models.audit_log import AuditLog
from app.models.activity import Activity


def generate_data():
    db = SessionLocal()

    try:
        # ============================================================
        # 1. DELETE EXISTING DATA
        # ============================================================
        # Delete child tables first because of foreign keys.

        db.query(Activity).delete()
        db.query(AuditLog).delete()
        db.query(Report).delete()
        db.query(Notification).delete()
        db.query(Renewal).delete()
        db.query(Obligation).delete()
        db.query(ContractVersion).delete()
        db.query(Contract).delete()
        db.query(User).delete()

        db.commit()

        print("Existing development data deleted.")

        # ============================================================
        # 2. USERS - 50 RECORDS
        # ============================================================

        users_data = [
            ("Ananya Sharma", "ananya.sharma@gmail.com", "Administrator"),
            ("Rahul Verma", "rahul.verma@gmail.com", "Employee"),
            ("Priya Nair", "priya.nair@gmail.com", "Legal Manager"),
            ("Arjun Menon", "arjun.menon@gmail.com", "Compliance Officer"),
            ("Sneha Iyer", "sneha.iyer@gmail.com", "Contract Manager"),
            ("Vikram Reddy", "vikram.reddy@gmail.com", "Department Head"),
            ("Kavya Krishnan", "kavya.krishnan@gmail.com", "Employee"),
            ("Rohan Mehta", "rohan.mehta@gmail.com", "Employee"),
            ("Meera Joshi", "meera.joshi@gmail.com", "Legal Manager"),
            ("Aditya Rao", "aditya.rao@gmail.com", "Contract Manager"),
            ("Divya Menon", "divya.menon@gmail.com", "Compliance Officer"),
            ("Karthik Nair", "karthik.nair@gmail.com", "Employee"),
            ("Neha Kapoor", "neha.kapoor@gmail.com", "Department Head"),
            ("Sanjay Kumar", "sanjay.kumar@gmail.com", "Employee"),
            ("Aishwarya Reddy", "aishwarya.reddy@gmail.com", "Legal Manager"),
            ("Manoj Iyer", "manoj.iyer@gmail.com", "Contract Manager"),
            ("Pooja Sharma", "pooja.sharma@gmail.com", "Compliance Officer"),
            ("Nikhil Verma", "nikhil.verma@gmail.com", "Employee"),
            ("Shreya Nair", "shreya.nair@gmail.com", "Department Head"),
            ("Varun Menon", "varun.menon@gmail.com", "Employee"),
            ("Ishita Rao", "ishita.rao@gmail.com", "Legal Manager"),
            ("Abhishek Joshi", "abhishek.joshi@gmail.com", "Employee"),
            ("Riya Kapoor", "riya.kapoor@gmail.com", "Contract Manager"),
            ("Harish Reddy", "harish.reddy@gmail.com", "Compliance Officer"),
            ("Nandini Krishnan", "nandini.krishnan@gmail.com", "Employee"),
            ("Suresh Babu", "suresh.babu@gmail.com", "Department Head"),
            ("Lakshmi Menon", "lakshmi.menon@gmail.com", "Legal Manager"),
            ("Akash Patel", "akash.patel@gmail.com", "Employee"),
            ("Swati Gupta", "swati.gupta@gmail.com", "Contract Manager"),
            ("Deepak Singh", "deepak.singh@gmail.com", "Compliance Officer"),
            ("Keerthi Nair", "keerthi.nair@gmail.com", "Employee"),
            ("Mohan Das", "mohan.das@gmail.com", "Department Head"),
            ("Tanvi Sharma", "tanvi.sharma@gmail.com", "Legal Manager"),
            ("Yash Verma", "yash.verma@gmail.com", "Employee"),
            ("Anjali Menon", "anjali.menon@gmail.com", "Contract Manager"),
            ("Rakesh Kumar", "rakesh.kumar@gmail.com", "Compliance Officer"),
            ("Bhavana Rao", "bhavana.rao@gmail.com", "Employee"),
            ("Girish Reddy", "girish.reddy@gmail.com", "Department Head"),
            ("Madhuri Iyer", "madhuri.iyer@gmail.com", "Legal Manager"),
            ("Siddharth Mehta", "siddharth.mehta@gmail.com", "Employee"),
            ("Nisha Kapoor", "nisha.kapoor@gmail.com", "Contract Manager"),
            ("Rajiv Sharma", "rajiv.sharma@gmail.com", "Compliance Officer"),
            ("Amrita Nair", "amrita.nair@gmail.com", "Employee"),
            ("Sandeep Menon", "sandeep.menon@gmail.com", "Department Head"),
            ("Harini Krishnan", "harini.krishnan@gmail.com", "Legal Manager"),
            ("Pranav Rao", "pranav.rao@gmail.com", "Employee"),
            ("Monika Joshi", "monika.joshi@gmail.com", "Contract Manager"),
            ("Gautam Verma", "gautam.verma@gmail.com", "Compliance Officer"),
            ("Reshma Iyer", "reshma.iyer@gmail.com", "Employee"),
            ("Amit Reddy", "amit.reddy@gmail.com", "Department Head"),
        ]

        users = []

        for full_name, email, role in users_data:
            user = User(
                full_name=full_name,
                email=email,
                password=hash_password("ContractIQ@123"),
                role=role,
                is_active=True
            )

            db.add(user)
            users.append(user)

        db.flush()

        print("50 users created.")

        # ============================================================
        # 3. CONTRACTS - 50 RECORDS
        # ============================================================

        contract_titles = [
            "Enterprise Software Licensing Agreement",
            "Cloud Infrastructure Services Agreement",
            "Data Processing and Protection Agreement",
            "Professional Consulting Services Agreement",
            "Office Facility Lease Agreement",
            "Cybersecurity Services Agreement",
            "IT Support and Maintenance Agreement",
            "Marketing Services Agreement",
            "Business Process Outsourcing Agreement",
            "Vendor Supply Agreement",
            "Enterprise Network Services Agreement",
            "Software Development Agreement",
            "Cloud Storage Services Agreement",
            "Human Resources Consulting Agreement",
            "Financial Advisory Services Agreement",
            "Equipment Maintenance Agreement",
            "Digital Marketing Services Agreement",
            "Customer Support Services Agreement",
            "Technology Partnership Agreement",
            "Information Security Agreement",
            "Legal Advisory Services Agreement",
            "Database Management Services Agreement",
            "Infrastructure Maintenance Agreement",
            "Professional Training Services Agreement",
            "Telecommunications Services Agreement",
            "Software Subscription Agreement",
            "Data Analytics Services Agreement",
            "Cloud Security Assessment Agreement",
            "Business Continuity Services Agreement",
            "Document Management Services Agreement",
            "Enterprise Resource Planning Agreement",
            "Quality Assurance Services Agreement",
            "Application Maintenance Agreement",
            "Network Security Monitoring Agreement",
            "Vendor Management Agreement",
            "Corporate Travel Services Agreement",
            "Recruitment Services Agreement",
            "Financial Audit Services Agreement",
            "Compliance Consulting Agreement",
            "Facilities Management Agreement",
            "IT Infrastructure Upgrade Agreement",
            "Enterprise Mobility Services Agreement",
            "Data Backup Services Agreement",
            "Software Testing Services Agreement",
            "Risk Management Consulting Agreement",
            "Cloud Migration Services Agreement",
            "Procurement Services Agreement",
            "Managed Security Services Agreement",
            "Business Intelligence Services Agreement",
            "Enterprise Support Agreement",
        ]

        categories = [
            "Technology",
            "Legal Services",
            "Compliance",
            "Consulting",
            "Facilities",
            "Cybersecurity",
            "IT Services",
            "Marketing",
            "Finance",
            "Procurement",
        ]

        statuses = [
            "Active",
            "Active",
            "Active",
            "Under Review",
            "Pending Approval",
            "Expired",
        ]

        contracts = []

        for i in range(50):
            start_date = date(2025, 1, 1) + timedelta(days=i * 12)
            end_date = start_date + timedelta(days=365)

            contract = Contract(
                title=contract_titles[i],
                contract_number=f"CIQ-2026-{i + 1:04d}",
                category=categories[i % len(categories)],
                status=statuses[i % len(statuses)],
                start_date=start_date,
                end_date=end_date,
                created_by=users[i % 50].id,
                assigned_to=users[(i + 1) % 50].id
            )

            db.add(contract)
            contracts.append(contract)

        db.flush()

        print("50 contracts created.")

        # ============================================================
        # 4. CONTRACT VERSIONS - 50 RECORDS
        # ============================================================

        for i in range(50):
            version = ContractVersion(
                contract_id=contracts[i].id,
                version_number=1,
                document_path=(
                    f"documents/contracts/"
                    f"CIQ-2026-{i + 1:04d}/version-1.pdf"
                ),
                created_by=users[(i + 2) % 50].id,
                created_at=datetime(2026, 1, 1) + timedelta(days=i)
            )

            db.add(version)

        db.flush()

        print("50 contract versions created.")

        # ============================================================
        # 5. OBLIGATIONS - 50 RECORDS
        # ============================================================

        obligation_titles = [
            "Annual Compliance Certification",
            "Quarterly Security Assessment",
            "Monthly Service Availability Report",
            "Data Protection Audit",
            "Insurance Certificate Renewal",
            "Payment Reconciliation",
            "Confidentiality Compliance Review",
            "Annual Contract Review",
            "Vendor Performance Assessment",
            "Security Incident Reporting",
            "Financial Statement Submission",
            "Employee Compliance Training",
            "Data Retention Review",
            "Service Level Monitoring",
            "Risk Assessment",
            "Regulatory Compliance Review",
            "Contract Documentation Update",
            "Access Control Review",
            "Business Continuity Test",
            "Backup Verification",
            "Software License Review",
            "Quality Assurance Audit",
            "Performance Report Submission",
            "Privacy Impact Assessment",
            "Supplier Certification Review",
            "Cybersecurity Policy Review",
            "Invoice Verification",
            "Asset Verification",
            "Legal Compliance Review",
            "Operational Risk Review",
            "Incident Response Testing",
            "System Availability Review",
            "Data Accuracy Validation",
            "Contract Performance Review",
            "Internal Control Assessment",
            "Security Patch Verification",
            "Third Party Risk Review",
            "Service Performance Audit",
            "Documentation Compliance Check",
            "Annual Policy Certification",
            "Regulatory Filing",
            "Training Completion Review",
            "Contract Renewal Preparation",
            "Financial Compliance Check",
            "Information Security Review",
            "Vendor Contract Review",
            "Data Privacy Certification",
            "Business Process Review",
            "Management Approval Review",
            "Final Compliance Assessment",
        ]

        obligation_types = [
            "Compliance",
            "Financial",
            "Security",
            "Reporting",
            "Legal",
            "Operational",
        ]

        obligation_statuses = [
            "Pending",
            "In Progress",
            "Completed",
            "Overdue",
        ]

        for i in range(50):
            obligation = Obligation(
                contract_id=contracts[i].id,
                title=obligation_titles[i],
                description=(
                    f"Complete {obligation_titles[i].lower()} "
                    f"for contract {contracts[i].contract_number}."
                ),
                obligation_type=obligation_types[
                    i % len(obligation_types)
                ],
                due_date=date(2026, 9, 1) + timedelta(days=i * 3),
                assigned_to=users[(i + 3) % 50].id,
                status=obligation_statuses[
                    i % len(obligation_statuses)
                ],
                progress=[0, 25, 50, 75, 100][i % 5]
            )

            db.add(obligation)

        db.flush()

        print("50 obligations created.")

        # ============================================================
        # 6. RENEWALS - 50 RECORDS
        # ============================================================

        renewal_statuses = [
            "Upcoming",
            "In Review",
            "Approved",
            "Pending",
            "Completed",
        ]

        approval_statuses = [
            "Pending",
            "Approved",
            "Rejected",
        ]

        for i in range(50):
            renewal = Renewal(
                contract_id=contracts[i].id,
                renewal_date=date(2027, 1, 1) + timedelta(days=i * 7),
                status=renewal_statuses[i % len(renewal_statuses)],
                approval_status=approval_statuses[
                    i % len(approval_statuses)
                ],
                notes=(
                    f"Renewal review for "
                    f"{contracts[i].contract_number}. "
                    "Required approvals and compliance checks "
                    "should be completed before the renewal date."
                )
            )

            db.add(renewal)

        db.flush()

        print("50 renewals created.")

        # ============================================================
        # 7. NOTIFICATIONS - 50 RECORDS
        # ============================================================

        notification_types = [
            "Renewal Reminder",
            "Obligation Due",
            "Contract Update",
            "Approval Required",
            "Compliance Alert",
            "System Notification",
        ]

        notification_titles = [
            "Contract Renewal Reminder",
            "Obligation Due Reminder",
            "Contract Update",
            "Contract Approval Required",
            "Compliance Alert",
            "System Notification",
        ]

        notification_messages = [
            "A contract renewal is approaching and requires review.",
            "An assigned obligation is approaching its due date.",
            "A contract has been updated and requires your attention.",
            "A contract approval is waiting for your action.",
            "A compliance review requires immediate attention.",
            "A new contract activity has been recorded.",
        ]

        for i in range(50):
            is_read = i % 3 == 0

            notification = Notification(
                user_id=users[i % 50].id,

                notification_type=notification_types[
                    i % len(notification_types)
                ],

                title=notification_titles[
                    i % len(notification_titles)
                ],

                message=notification_messages[
                    i % len(notification_messages)
                ],

                status="Read" if is_read else "Unread",

                scheduled_at=None,

                sent_at=(
                    datetime(2026, 7, 1)
                    + timedelta(days=i)
                ),

                read_at=(
                    datetime(2026, 7, 1)
                    + timedelta(days=i)
                    if is_read
                    else None
                ),

                created_at=(
                    datetime(2026, 7, 1)
                    + timedelta(days=i)
                ),

                updated_at=(
                    datetime(2026, 7, 1)
                    + timedelta(days=i)
                ),
            )

            db.add(notification)

        db.flush()

        print("50 notifications created.")

        # ============================================================
        # 8. REPORTS - 50 RECORDS
        # ============================================================

        report_types = [
            "Contract Summary",
            "Obligation Compliance Report",
            "Renewal Status Report",
            "Contract Expiry Report",
            "Compliance Risk Report",
            "Audit Activity Report",
            "Contract Performance Report",
        ]

        file_formats = [
            "PDF",
            "Excel",
            "CSV",
        ]

        for i in range(50):
            report = Report(
                report_type=report_types[
                    i % len(report_types)
                ],
                generated_by=users[(i + 4) % 50].id,
                file_format=file_formats[
                    i % len(file_formats)
                ],
                file_path=(
                    f"reports/2026/"
                    f"report-{i + 1:04d}.pdf"
                ),
                created_at=(
                    datetime(2026, 7, 1)
                    + timedelta(days=i)
                )
            )

            db.add(report)

        db.flush()

        print("50 reports created.")

        # ============================================================
        # 9. AUDIT LOGS - 50 RECORDS
        # ============================================================

        actions = [
            "CREATE",
            "UPDATE",
            "DELETE",
            "LOGIN",
            "CONTRACT_CREATED",
            "CONTRACT_UPDATED",
            "OBLIGATION_UPDATED",
            "REPORT_GENERATED",
            "RENEWAL_REVIEWED",
            "USER_UPDATED",
        ]

        entity_types = [
            "User",
            "Contract",
            "Obligation",
            "Renewal",
            "Report",
            "Notification",
        ]

        for i in range(50):
            audit_log = AuditLog(
                user_id=users[i % 50].id,
                action=actions[
                    i % len(actions)
                ],
                entity_type=entity_types[
                    i % len(entity_types)
                ],
                details=(
                    f"User {users[i % 50].full_name} performed "
                    f"{actions[i % len(actions)].lower()} action "
                    f"on a "
                    f"{entity_types[i % len(entity_types)].lower()}."
                ),
                created_at=(
                    datetime(2026, 7, 1)
                    + timedelta(hours=i * 5)
                )
            )

            db.add(audit_log)

        db.flush()

        print("50 audit logs created.")

        # ============================================================
        # 10. ACTIVITIES - 50 RECORDS
        # ============================================================

        activity_types = [
            "Contract Created",
            "Contract Updated",
            "Version Uploaded",
            "Obligation Reviewed",
            "Report Generated",
            "Renewal Updated",
            "Compliance Review",
            "User Login",
        ]

        activity_descriptions = [
            "Created a new contract record.",
            "Updated contract information.",
            "Uploaded a new contract version.",
            "Reviewed an assigned obligation.",
            "Generated a compliance report.",
            "Updated renewal information.",
            "Completed a compliance review.",
            "Logged into the ContractIQ platform.",
        ]

        for i in range(50):
            activity = Activity(
                user_id=users[i % 50].id,
                activity_type=activity_types[
                    i % len(activity_types)
                ],
                description=activity_descriptions[
                    i % len(activity_descriptions)
                ],
                created_at=(
                    datetime(2026, 7, 1)
                    + timedelta(hours=i * 4)
                )
            )

            db.add(activity)

        db.flush()

        print("50 activities created.")

        # ============================================================
        # COMMIT EVERYTHING
        # ============================================================

        db.commit()

        print("\n==========================================")
        print("50-ROW DATA GENERATION COMPLETED")
        print("==========================================")
        print("Users:              50")
        print("Contracts:          50")
        print("Contract Versions:  50")
        print("Obligations:        50")
        print("Renewals:           50")
        print("Notifications:      50")
        print("Reports:            50")
        print("Audit Logs:         50")
        print("Activities:         50")
        print("==========================================")
        print("\nRBAC test accounts:")
        print("Administrator: ananya.sharma@gmail.com")
        print("Employee:      rahul.verma@gmail.com")
        print("Password:      ContractIQ@123")
        print("==========================================")

    except Exception as error:
        db.rollback()
        print("\nData generation failed.")
        print(error)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    generate_data()