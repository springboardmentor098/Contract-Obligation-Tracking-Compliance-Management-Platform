import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ComplianceRecord {
  contract_id: number;
  contract_number: string;
  compliance_status: string;
  compliance_score: number;
  total_obligations: number;
  completed_obligations: number;
  pending_obligations: number;
  overdue_obligations: number;
  risk_level: string;
}

export interface ComplianceSummary {
  total_contracts: number;
  compliant_contracts: number;
  pending_contracts: number;
  delayed_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
}

@Injectable({
  providedIn: 'root'
})
export class ComplianceService {

  private apiUrl = 'http://127.0.0.1:8000/compliance';

  constructor(private http: HttpClient) {}

  getComplianceRecords(): Observable<ComplianceRecord[]> {
    return this.http.get<ComplianceRecord[]>(
      this.apiUrl
    );
  }

  getComplianceSummary(): Observable<ComplianceSummary> {
    return this.http.get<ComplianceSummary>(
      `${this.apiUrl}/summary`
    );
  }

  getNonCompliantContracts(): Observable<ComplianceRecord[]> {
    return this.http.get<ComplianceRecord[]>(
      `${this.apiUrl}/non-compliant`
    );
  }

  getHighRiskContracts(): Observable<ComplianceRecord[]> {
    return this.http.get<ComplianceRecord[]>(
      `${this.apiUrl}/high-risk`
    );
  }

  getComplianceHistory(contractId: number): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.apiUrl}/${contractId}/history`
    );
  }
}
