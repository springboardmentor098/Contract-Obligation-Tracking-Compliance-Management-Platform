import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ComplianceRecord {
  contract_id: string | number;
  contract_number: string | null;
  compliance_status: string | null;
  compliance_score: number | null;
  total_obligations: number;
  completed_obligations: number;
  pending_obligations: number;
  overdue_obligations: number;
  risk_level: string | null;
}

export interface ComplianceSummary {
  total_contracts: number;
  compliant_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
  average_compliance_score: number;
}

export interface NonCompliantContract {
  contract_id: string | number;
  contract_number: string | null;
  compliance_status: string | null;
  overdue_obligations: number;
}

export interface HighRiskContract {
  contract_id: string | number;
  contract_number: string | null;
  risk_level: string | null;
  overdue_obligations: number;
}

export interface ComplianceHistory {
  id: string;
  contract_id: string | number;
  compliance_status: string | null;
  compliance_score: number | null;
  risk_level: string | null;
  total_obligations: number;
  completed_obligations: number;
  pending_obligations: number;
  overdue_obligations: number;
  evaluated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class ComplianceService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    'http://127.0.0.1:8000/compliance';

  /**
   * Get all compliance records available
   * to the logged-in user.
   */
  getAllCompliance(): Observable<ComplianceRecord[]> {
    return this.http.get<ComplianceRecord[]>(
      this.apiUrl
    );
  }

  /**
   * Get compliance summary.
   */
  getSummary(): Observable<ComplianceSummary> {
    return this.http.get<ComplianceSummary>(
      `${this.apiUrl}/summary`
    );
  }

  /**
   * Get non-compliant contracts.
   */
  getNonCompliantContracts():
    Observable<NonCompliantContract[]> {

    return this.http.get<NonCompliantContract[]>(
      `${this.apiUrl}/non-compliant`
    );
  }

  /**
   * Get high-risk contracts.
   */
  getHighRiskContracts():
    Observable<HighRiskContract[]> {

    return this.http.get<HighRiskContract[]>(
      `${this.apiUrl}/high-risk`
    );
  }

  /**
   * Get compliance information for one contract.
   */
  getContractCompliance(
    contractId: string
  ): Observable<ComplianceRecord> {

    return this.http.get<ComplianceRecord>(
      `${this.apiUrl}/contracts/${contractId}`
    );
  }

  /**
   * Evaluate/recalculate compliance for a contract.
   */
  evaluateContract(
    contractId: string
  ): Observable<ComplianceRecord> {

    return this.http.post<ComplianceRecord>(
      `${this.apiUrl}/contracts/${contractId}/evaluate`,
      {}
    );
  }

  /**
   * Get compliance evaluation history for a contract.
   */
  getComplianceHistory(
    contractId: string
  ): Observable<ComplianceHistory[]> {

    return this.http.get<ComplianceHistory[]>(
      `${this.apiUrl}/contracts/${contractId}/history`
    );
  }
}