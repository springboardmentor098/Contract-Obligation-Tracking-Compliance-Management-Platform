from datetime import date
from app.models import Obligation

def effective_status(obligation: Obligation, today: date|None=None):
    today=today or date.today()
    if obligation.status != "Completed" and obligation.due_date < today:
        return "Overdue"
    return obligation.status

def refresh_overdue(obligation, today=None):
    s=effective_status(obligation,today)
    if s=="Overdue": obligation.status="Overdue"
    return obligation
