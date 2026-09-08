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
  pending_contracts: number;
  delayed_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
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

@Injectable({
  providedIn: 'root'
})
export class ComplianceService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    'http://127.0.0.1:8000/compliance';

  getAllCompliance(): Observable<ComplianceRecord[]> {
    return this.http.get<ComplianceRecord[]>(
      this.apiUrl
    );
  }

  getSummary(): Observable<ComplianceSummary> {
    return this.http.get<ComplianceSummary>(
      `${this.apiUrl}/summary`
    );
  }

  getNonCompliantContracts():
    Observable<NonCompliantContract[]> {

    return this.http.get<NonCompliantContract[]>(
      `${this.apiUrl}/non-compliant`
    );
  }

  getHighRiskContracts():
    Observable<HighRiskContract[]> {

    return this.http.get<HighRiskContract[]>(
      `${this.apiUrl}/high-risk`
    );
  }

  getContractCompliance(
    contractId: string
  ): Observable<ComplianceRecord> {

    return this.http.get<ComplianceRecord>(
      `http://127.0.0.1:8000/contracts/${contractId}/compliance`
    );
  }
}