from datetime import date, datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.compliance import ComplianceRecord
from app.schemas.compliance import (
    ComplianceHistoryResponse,
    ComplianceListItemResponse,
    ComplianceSummaryResponse,
    ContractComplianceResponse,
    HighRiskContractResponse,
    NonCompliantContractResponse,
)


def evaluate_contract_compliance(contract_id: int, db: Session) -> ComplianceRecord:
    """
    Evaluates obligations for a contract, calculates compliance score, status, and risk level,
    and stores an evaluation snapshot in compliance_records for audit tracking.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    obligations = db.query(Obligation).filter(Obligation.contract_id == contract_id).all()
    today = date.today()

    total_obligations = len(obligations)
    completed_obligations = 0
    pending_obligations = 0
    overdue_obligations = 0
    delayed_obligations = 0

    for ob in obligations:
        st = ob.status.strip() if ob.status else "Pending"
        due = ob.due_date

        if st == "Completed":
            completed_obligations += 1
        elif st == "Overdue" or (due is not None and due < today and st != "Completed"):
            overdue_obligations += 1
        elif st in ["Delayed", "In Progress"]:
            delayed_obligations += 1
        else:  # Pending
            pending_obligations += 1

    # 1. Compliance Score
    if total_obligations == 0:
        compliance_score = 100.0
    else:
        compliance_score = round((completed_obligations / total_obligations) * 100.0, 2)

    # 2. Risk Level
    if overdue_obligations >= 2:
        risk_level = "High"
    elif overdue_obligations == 1:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # 3. Compliance Status
    if total_obligations == 0 or completed_obligations == total_obligations:
        compliance_status = "Compliant"
    elif overdue_obligations >= 2 or (overdue_obligations >= 1 and compliance_score < 60):
        compliance_status = "High Risk"
    elif overdue_obligations >= 1:
        compliance_status = "Non-Compliant"
    elif delayed_obligations >= 1:
        compliance_status = "Delayed"
    else:
        compliance_status = "Pending"

    # 4. Save evaluation snapshot in database
    evaluation_record = ComplianceRecord(
        contract_id=contract_id,
        compliance_status=compliance_status,
        compliance_score=compliance_score,
        risk_level=risk_level,
        total_obligations=total_obligations,
        completed_obligations=completed_obligations,
        pending_obligations=pending_obligations,
        overdue_obligations=overdue_obligations,
        delayed_obligations=delayed_obligations,
        evaluated_at=datetime.utcnow(),
        notes=f"Evaluated at {datetime.utcnow().isoformat()}. Score: {compliance_score}%, Status: {compliance_status}, Risk: {risk_level}"
    )

    db.add(evaluation_record)
    db.commit()
    db.refresh(evaluation_record)

    return evaluation_record


def get_all_compliance_records(db: Session) -> List[ComplianceListItemResponse]:
    """Retrieves current compliance evaluation for all contracts."""
    contracts = db.query(Contract).all()
    result = []
    for contract in contracts:
        record = evaluate_contract_compliance(contract.id, db)
        result.append(ComplianceListItemResponse(
            contract_id=contract.id,
            contract_number=contract.contract_number,
            title=contract.title,
            compliance_status=record.compliance_status,
            compliance_score=record.compliance_score,
            risk_level=record.risk_level,
            overdue_obligations=record.overdue_obligations
        ))
    return result


def get_compliance_summary(db: Session) -> ComplianceSummaryResponse:
    """Provides overall compliance statistics across all contracts."""
    contracts = db.query(Contract).all()
    total_contracts = len(contracts)

    if total_contracts == 0:
        return ComplianceSummaryResponse(
            total_contracts=0,
            compliant_contracts=0,
            pending_contracts=0,
            delayed_contracts=0,
            non_compliant_contracts=0,
            high_risk_contracts=0,
            average_compliance_score=100.0
        )

    compliant_count = 0
    pending_count = 0
    delayed_count = 0
    non_compliant_count = 0
    high_risk_count = 0
    total_score = 0.0

    for c in contracts:
        rec = evaluate_contract_compliance(c.id, db)
        total_score += rec.compliance_score
        st = rec.compliance_status

        if st == "Compliant":
            compliant_count += 1
        elif st == "Pending":
            pending_count += 1
        elif st == "Delayed":
            delayed_count += 1
        elif st == "Non-Compliant":
            non_compliant_count += 1
        elif st == "High Risk":
            high_risk_count += 1

    avg_score = round(total_score / total_contracts, 2)

    return ComplianceSummaryResponse(
        total_contracts=total_contracts,
        compliant_contracts=compliant_count,
        pending_contracts=pending_count,
        delayed_contracts=delayed_count,
        non_compliant_contracts=non_compliant_count,
        high_risk_contracts=high_risk_count,
        average_compliance_score=avg_score
    )


def get_non_compliant_contracts(db: Session) -> List[NonCompliantContractResponse]:
    """Retrieves contracts with non-compliant status or overdue obligations."""
    contracts = db.query(Contract).all()
    non_compliant_list = []

    for c in contracts:
        rec = evaluate_contract_compliance(c.id, db)
        if rec.compliance_status in ["Non-Compliant", "High Risk"] or rec.overdue_obligations > 0:
            non_compliant_list.append(NonCompliantContractResponse(
                contract_id=c.id,
                contract_number=c.contract_number,
                title=c.title,
                compliance_status=rec.compliance_status,
                compliance_score=rec.compliance_score,
                overdue_obligations=rec.overdue_obligations,
                risk_level=rec.risk_level
            ))

    return non_compliant_list


def get_high_risk_contracts(db: Session) -> List[HighRiskContractResponse]:
    """Retrieves contracts identified with High risk level."""
    contracts = db.query(Contract).all()
    high_risk_list = []

    for c in contracts:
        rec = evaluate_contract_compliance(c.id, db)
        if rec.risk_level == "High" or rec.compliance_status == "High Risk":
            high_risk_list.append(HighRiskContractResponse(
                contract_id=c.id,
                contract_number=c.contract_number,
                title=c.title,
                risk_level=rec.risk_level,
                overdue_obligations=rec.overdue_obligations,
                compliance_score=rec.compliance_score,
                compliance_status=rec.compliance_status
            ))

    return high_risk_list


def get_contract_compliance_history(contract_id: int, db: Session) -> List[ComplianceRecord]:
    """Retrieves full evaluation audit history for a contract."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    history = db.query(ComplianceRecord).filter(
        ComplianceRecord.contract_id == contract_id
    ).order_by(ComplianceRecord.evaluated_at.desc()).all()

    return history
