import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface ContractReportItem {
  id: number;
  contract_number: string;
  title: string;
  category: string;
  start_date: string;
  end_date: string;
  status: string;
  created_by: number;
  assigned_to?: number | null;
}

export interface ContractReport {
  total_contracts: number;
  active_contracts: number;
  expired_contracts: number;
  pending_approval_contracts: number;
  contracts_by_status: Record<string, number>;
  contract_records: ContractReportItem[];
}

export interface ObligationReportItem {
  id: number;
  contract_id: number;
  contract_number?: string | null;
  contract_title?: string | null;
  title: string;
  description?: string | null;
  obligation_type: string;
  due_date: string;
  assigned_to?: number | null;
  status: string;
  completion_date?: string | null;
}

export interface ObligationReport {
  total_obligations: number;
  pending_obligations: number;
  completed_obligations: number;
  overdue_obligations: number;
  obligations_by_status: Record<string, number>;
  obligation_records: ObligationReportItem[];
}

export interface RenewalReportItem {
  contract_id: number;
  contract_number?: string | null;
  contract_title?: string | null;
  expiry_date?: string | null;
  renewal_date?: string | null;
  days_remaining?: number | null;
  status: string;
}

export interface RenewalReport {
  upcoming_renewals: number;
  expired_contracts: number;
  immediate_attention: number;
  renewal_records: RenewalReportItem[];
}

export interface ComplianceReportItem {
  contract_id: number;
  contract_number?: string | null;
  contract_title?: string | null;

  total_obligations: number;
  completed_obligations: number;
  pending_obligations: number;
  delayed_obligations: number;
  overdue_obligations: number;

  compliance_score: number;
  compliance_status: string;
  risk_level: string;
}

export interface ComplianceReport {
  total_contracts: number;
  compliant_contracts: number;
  pending_contracts: number;
  delayed_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
  compliance_percentage: number;
  compliance_records: ComplianceReportItem[];
}

@Injectable({
  providedIn: 'root'
})
export class ReportService {

  private readonly api = inject(ApiService);

  contracts(): Observable<ContractReport> {
    return this.api.get<ContractReport>(
      '/reports/contracts'
    );
  }

  obligations(): Observable<ObligationReport> {
    return this.api.get<ObligationReport>(
      '/reports/obligations'
    );
  }

  renewals(): Observable<RenewalReport> {
    return this.api.get<RenewalReport>(
      '/reports/renewals'
    );
  }

  compliance(): Observable<ComplianceReport> {
    return this.api.get<ComplianceReport>(
      '/reports/compliance'
    );
  }

  dashboard<T = unknown>(): Observable<T> {
    return this.api.get<T>(
      '/reports/dashboard'
    );
  }

  summary<T = unknown>(): Observable<T> {
    return this.api.get<T>(
      '/reports/summary'
    );
  }
}
