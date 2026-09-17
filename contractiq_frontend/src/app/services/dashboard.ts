import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DashboardSummary {
  total_contracts: number;
  active_contracts: number;
  draft_contracts: number;
  contracts_under_review: number;
  upcoming_renewals: number;
  expired_contracts: number;
  total_obligations: number;
  pending_obligations: number;
  overdue_obligations: number;
  completed_obligations: number;
  compliant_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
}

export interface ContractStats {
  total: number;
  active: number;
  draft: number;
  under_review: number;
  approved: number;
  expired: number;
  terminated: number;
  by_category: { [key: string]: number };
}

export interface ObligationStats {
  total: number;
  pending: number;
  in_progress: number;
  completed: number;
  delayed: number;
  overdue: number;
}

export interface ComplianceStats {
  total_evaluated: number;
  compliant: number;
  pending: number;
  delayed: number;
  non_compliant: number;
  high_risk: number;
  average_compliance_score: number | null;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getDashboardSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(
      `${this.apiUrl}/dashboard/summary`
    );
  }

  getContractStats(): Observable<ContractStats> {
    return this.http.get<ContractStats>(
      `${this.apiUrl}/reports/contracts/summary`
    );
  }

  getObligationStats(): Observable<ObligationStats> {
    return this.http.get<ObligationStats>(
      `${this.apiUrl}/reports/obligations/summary`
    );
  }

  getComplianceStats(): Observable<ComplianceStats> {
    return this.http.get<ComplianceStats>(
      `${this.apiUrl}/reports/compliance/summary`
    );
  }
}