import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ContractAnalytics {
  total: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  by_counterparty: Record<string, number>;
  expiring_next_30_days: number;
  expiring_next_90_days: number;
}

export interface ObligationAnalytics {
  total: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_responsible_party: Record<string, number>;
  overdue: number;
  due_next_7_days: number;
  due_next_30_days: number;
}

export interface RenewalAnalytics {
  total: number;
  by_status: Record<string, number>;
  due_next_7_days: number;
  due_next_30_days: number;
  due_next_90_days: number;
  overdue: number;
  by_contract: Record<string, number>;
}

export interface ComplianceAnalytics {
  total_contracts: number;
  compliant_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
  compliance_rate: number;
  overdue_obligations: number;
  high_priority_overdue_obligations: number;
}

export interface DashboardSummary {
  contracts: {
    total: number;
    active: number;
    draft: number;
    under_review: number;
    expired: number;
  };
  obligations: {
    total: number;
    pending: number;
    overdue: number;
    completed: number;
  };
  renewals: {
    total: number;
    upcoming: number;
    completed: number;
  };
  compliance: {
    compliant_contracts: number;
    non_compliant_contracts: number;
    high_risk_contracts: number;
  };
}

@Injectable({
  providedIn: 'root'
})
export class ReportService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  getContractAnalytics(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/reports/analytics/contracts`
    );
  }

  getObligationAnalytics(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/reports/analytics/obligations`
    );
  }

  getRenewalAnalytics(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/reports/analytics/renewals`
    );
  }

  getComplianceAnalytics(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/reports/analytics/compliance`
    );
  }

  getDashboardSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(
      `${this.apiUrl}/reports/dashboard/summary`
    );
  }

  exportContractsExcel(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/export/contracts/excel`,
      { responseType: 'blob' }
    );
  }

  exportContractsPdf(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/export/contracts/pdf`,
      { responseType: 'blob' }
    );
  }

  exportObligationsExcel(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/export/obligations/excel`,
      { responseType: 'blob' }
    );
  }

  exportRenewalsExcel(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/export/renewals/excel`,
      { responseType: 'blob' }
    );
  }

  exportDashboardPdf(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/export/dashboard/pdf`,
      { responseType: 'blob' }
    );
  }
}
