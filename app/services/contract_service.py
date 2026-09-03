from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Contract
from app.schemas.contract import CATEGORIES
TRANSITIONS={"Draft":{"Under Review"},"Under Review":{"Approved"},"Approved":{"Active"},"Active":{"Expired","Terminated"}}
def transition(contract,status):
    if status not in TRANSITIONS.get(contract.status,set()): raise HTTPException(400,f"Invalid status transition: {contract.status} -> {status}")
    contract.status=status
    now=datetime.now(timezone.utc)
    if status=="Under Review": contract.reviewed_at=now
    if status=="Approved": contract.approved_at=now
    return contract

def can_manage(user, contract):
    return user.role in {"Administrator","Legal Manager","Contract Manager"} or contract.created_by==user.id or contract.assigned_to==user.id
