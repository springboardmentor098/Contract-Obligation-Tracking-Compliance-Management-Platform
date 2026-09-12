import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Compliance {
  contract_id: number;
  contract_number: string;
  compliance_status: string;
  compliance_score: number;
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

export interface ContractCompliance {
  contract_id: number;
  compliance_status: string;
  compliance_score: number;
  total_obligations: number;
  completed_obligations: number;
  pending_obligations: number;
  overdue_obligations: number;
  risk_level: string;
}

export interface ComplianceHistory {
  id: number;
  contract_id: number;
  compliance_status: string;
  compliance_score: number;
  total_obligations: number;
  completed_obligations: number;
  pending_obligations: number;
  overdue_obligations: number;
  risk_level: string;
  evaluated_by: number;
  evaluated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class Compliance {

  private readonly baseUrl = 'http://127.0.0.1:8000/compliance';

  constructor(private http: HttpClient) {}

  getCompliance(): Observable<Compliance[]> {
    return this.http.get<Compliance[]>(this.baseUrl);
  }

  getComplianceSummary(): Observable<ComplianceSummary> {
    return this.http.get<ComplianceSummary>(
      `${this.baseUrl}/summary`
    );
  }

  getNonCompliant(): Observable<Compliance[]> {
    return this.http.get<Compliance[]>(
      `${this.baseUrl}/non-compliant`
    );
  }

  getHighRisk(): Observable<Compliance[]> {
    return this.http.get<Compliance[]>(
      `${this.baseUrl}/high-risk`
    );
  }

  getContractCompliance(
    contractId: number
  ): Observable<ContractCompliance> {
    return this.http.get<ContractCompliance>(
      `${this.baseUrl}/contracts/${contractId}/compliance`
    );
  }

  getComplianceHistory(
    contractId: number
  ): Observable<ComplianceHistory[]> {
    return this.http.get<ComplianceHistory[]>(
      `${this.baseUrl}/contract/${contractId}/history`
    );
  }
}