import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ContractSummary {
  total_contracts: number;
  active_contracts: number;
  expired_contracts: number;
  pending_approval: number;
}

export interface ObligationSummary {
  total_obligations: number;
  pending_obligations: number;
  completed_obligations: number;
  overdue_obligations: number;
}

export interface RenewalSummary {
  upcoming_renewals: any[];
  expired_contracts: number;
  contracts_requiring_attention: number;
}

export interface ComplianceSummary {
  total_contracts: number;
  compliant_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
  high_risk_obligations: number;
  average_compliance_score: number;
}

export interface StatusCount {
  status: string;
  count: number;
}

export interface DashboardResponse {
  contracts: ContractSummary;
  contract_status_distribution: StatusCount[];
  obligations: ObligationSummary;
  obligation_status_distribution: StatusCount[];
  renewals: RenewalSummary;
  compliance: ComplianceSummary;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://localhost:8000/reports';

  getDashboard(): Observable<DashboardResponse> {
    return this.http.get<DashboardResponse>(
      `${this.apiUrl}/dashboard`
    );
  }
}