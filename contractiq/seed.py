from datetime import date,timedelta
from app.database import SessionLocal
from app.models import User,Contract,Obligation,Renewal
from app.core.security import hash_password

def main():
 db=SessionLocal()
 try:
  if not db.query(User).filter_by(email="admin@contractiq.local").first():
   admin=User(full_name="ContractIQ Admin",email="admin@contractiq.local",hashed_password=hash_password("Admin@12345"),role="Administrator")
   employee=User(full_name="Demo Employee",email="employee@contractiq.local",hashed_password=hash_password("Employee@12345"),role="Employee")
   db.add_all([admin,employee]); db.commit(); db.refresh(admin); db.refresh(employee)
  else: admin=db.query(User).filter_by(email="admin@contractiq.local").first(); employee=db.query(User).filter_by(email="employee@contractiq.local").first()
  if not db.query(Contract).filter_by(contract_number="CNT-1001").first():
   c=Contract(title="ABC Vendor Agreement",contract_number="CNT-1001",category="Vendor Contract",description="Annual vendor service agreement",start_date=date.today(),end_date=date.today()+timedelta(days=30),status="Draft",created_by=admin.id,assigned_to=employee.id)
   db.add(c); db.commit(); db.refresh(c)
   db.add(Obligation(contract_id=c.id,title="Submit Monthly Service Report",description="Vendor submits monthly report",obligation_type="Reporting Requirement",due_date=date.today()+timedelta(days=7),assigned_to=employee.id,status="Pending"))
   db.add(Renewal(contract_id=c.id,renewal_date=c.end_date-timedelta(days=30),previous_expiry_date=c.end_date,status="Upcoming",assigned_to=admin.id,notes="Annual renewal")); db.commit()
 finally: db.close()
 print("Seed complete. Admin: admin@contractiq.local / Admin@12345")
if __name__=="__main__": main()
