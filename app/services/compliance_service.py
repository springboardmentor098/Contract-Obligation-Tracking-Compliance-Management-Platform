from sqlalchemy.orm import Session
from app.models.all_models import Obligation, Contract, ComplianceRecord, ComplianceStatusEnum, RiskLevelEnum, ObligationStatus

def evaluate_contract_compliance(db: Session, contract_id: int):
    """Calculates compliance score, determines risk, and logs history."""
    obligations = db.query(Obligation).filter(Obligation.contract_id == contract_id).all()
    total = len(obligations)
    
    # Default values for contracts with no obligations
    if total == 0:
        return {
            "contract_id": contract_id,
            "compliance_status": ComplianceStatusEnum.PENDING,
            "compliance_score": 0,
            "total_obligations": 0,
            "completed_obligations": 0,
            "pending_obligations": 0,
            "overdue_obligations": 0,
            "risk_level": RiskLevelEnum.LOW
        }

    # Count obligations by status
    completed = sum(1 for o in obligations if o.status == ObligationStatus.COMPLETED)
    overdue = sum(1 for o in obligations if o.status == ObligationStatus.OVERDUE)
    pending = sum(1 for o in obligations if o.status in [ObligationStatus.PENDING, ObligationStatus.IN_PROGRESS])
    
    # Calculate Math Score
    score = int((completed / total) * 100)
    
    # Business Logic for Risk & Status
    if overdue > 1:
        status = ComplianceStatusEnum.HIGH_RISK
        risk = RiskLevelEnum.HIGH
    elif overdue == 1:
        status = ComplianceStatusEnum.NON_COMPLIANT
        risk = RiskLevelEnum.MEDIUM
    elif pending > 0:
        status = ComplianceStatusEnum.PENDING
        risk = RiskLevelEnum.LOW
    else:
        status = ComplianceStatusEnum.COMPLIANT
        risk = RiskLevelEnum.LOW
        
    # Maintain Audit History (Save a record to the DB)
    record = ComplianceRecord(
        contract_id=contract_id,
        status=status,
        compliance_score=score,
        risk_level=risk
    )
    db.add(record)
    db.commit()
    
    return {
        "contract_id": contract_id,
        "compliance_status": status,
        "compliance_score": score,
        "total_obligations": total,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "overdue_obligations": overdue,
        "risk_level": risk
    }