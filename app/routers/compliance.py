from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.all_models import Contract, ComplianceRecord, ComplianceStatusEnum, RiskLevelEnum
from app.schemas.compliance import (
    ContractComplianceResponse,
    ComplianceSummaryResponse,
    ContractRiskResponse,
    ComplianceRecordResponse
)
from app.core.security import get_current_user
from app.services.compliance_service import evaluate_contract_compliance

router = APIRouter(tags=["Compliance"])

# 1. API 1: Get Contract Compliance (Dynamically calculates and returns)
@router.get("/contracts/{contract_id}/compliance", response_model=ContractComplianceResponse, status_code=status.HTTP_200_OK)
def get_contract_compliance(contract_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract Not Found")
    
    return evaluate_contract_compliance(db, contract_id)

# 2. API 2: Get All Compliance History Records
@router.get("/compliance", response_model=List[ComplianceRecordResponse], status_code=status.HTTP_200_OK)
def get_all_compliance_history(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(ComplianceRecord).all()

# 3. API 3: Get Compliance Summary (For the Dashboard)
@router.get("/compliance/summary", response_model=ComplianceSummaryResponse, status_code=status.HTTP_200_OK)
def get_compliance_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    contracts = db.query(Contract).all()
    
    summary = {
        "total_contracts": len(contracts),
        "compliant_contracts": 0,
        "pending_contracts": 0,
        "delayed_contracts": 0,
        "non_compliant_contracts": 0,
        "high_risk_contracts": 0
    }
    
    for contract in contracts:
        comp_data = evaluate_contract_compliance(db, contract.id)
        status_val = comp_data["compliance_status"]
        
        if status_val == ComplianceStatusEnum.COMPLIANT:
            summary["compliant_contracts"] += 1
        elif status_val == ComplianceStatusEnum.PENDING:
            summary["pending_contracts"] += 1
        elif status_val == ComplianceStatusEnum.DELAYED:
            summary["delayed_contracts"] += 1
        elif status_val == ComplianceStatusEnum.NON_COMPLIANT:
            summary["non_compliant_contracts"] += 1
        elif status_val == ComplianceStatusEnum.HIGH_RISK:
            summary["high_risk_contracts"] += 1

    return summary

# 4. API 4: Get Non-Compliant Contracts
@router.get("/compliance/non-compliant", response_model=List[ContractRiskResponse], status_code=status.HTTP_200_OK)
def get_non_compliant_contracts(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    contracts = db.query(Contract).all()
    results = []
    
    for contract in contracts:
        comp_data = evaluate_contract_compliance(db, contract.id)
        if comp_data["compliance_status"] == ComplianceStatusEnum.NON_COMPLIANT:
            results.append({
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "compliance_status": comp_data["compliance_status"],
                "risk_level": comp_data["risk_level"],
                "overdue_obligations": comp_data["overdue_obligations"]
            })
    return results

# 5. API 5: Get High-Risk Contracts
@router.get("/compliance/high-risk", response_model=List[ContractRiskResponse], status_code=status.HTTP_200_OK)
def get_high_risk_contracts(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    contracts = db.query(Contract).all()
    results = []
    
    for contract in contracts:
        comp_data = evaluate_contract_compliance(db, contract.id)
        if comp_data["compliance_status"] == ComplianceStatusEnum.HIGH_RISK:
            results.append({
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "compliance_status": comp_data["compliance_status"],
                "risk_level": comp_data["risk_level"],
                "overdue_obligations": comp_data["overdue_obligations"]
            })
    return results