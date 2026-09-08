import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface StatusCount {
  status: string;
  count: number;
}

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

export interface RenewalReportItem {
  id: string;
  contract_id: string;
  renewal_date: string | null;
  previous_expiry_date: string | null;
  new_expiry_date: string | null;
  status: string;
}

export interface RenewalSummary {
  upcoming_renewals: RenewalReportItem[];
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

export interface DashboardReport {
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
export class ReportService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://127.0.0.1:8000/reports';

  getContractSummary(
    contractStatus?: string,
    dateFrom?: string,
    dateTo?: string
  ): Observable<ContractSummary> {
    let params = new HttpParams();

    if (contractStatus) {
      params = params.set('contract_status', contractStatus);
    }

    if (dateFrom) {
      params = params.set('date_from', dateFrom);
    }

    if (dateTo) {
      params = params.set('date_to', dateTo);
    }

    return this.http.get<ContractSummary>(
      `${this.apiUrl}/contracts/summary`,
      { params }
    );
  }

  getContractStatusDistribution(
    contractStatus?: string
  ): Observable<{ data: StatusCount[] }> {
    let params = new HttpParams();

    if (contractStatus) {
      params = params.set('contract_status', contractStatus);
    }

    return this.http.get<{ data: StatusCount[] }>(
      `${this.apiUrl}/contracts/status-distribution`,
      { params }
    );
  }

  getObligationSummary(
    obligationStatus?: string,
    contractStatus?: string
  ): Observable<ObligationSummary> {
    let params = new HttpParams();

    if (obligationStatus) {
      params = params.set('obligation_status', obligationStatus);
    }

    if (contractStatus) {
      params = params.set('contract_status', contractStatus);
    }

    return this.http.get<ObligationSummary>(
      `${this.apiUrl}/obligations/summary`,
      { params }
    );
  }

  getObligationStatusDistribution(
    obligationStatus?: string,
    contractStatus?: string
  ): Observable<{ data: StatusCount[] }> {
    let params = new HttpParams();

    if (obligationStatus) {
      params = params.set('obligation_status', obligationStatus);
    }

    if (contractStatus) {
      params = params.set('contract_status', contractStatus);
    }

    return this.http.get<{ data: StatusCount[] }>(
      `${this.apiUrl}/obligations/status-distribution`,
      { params }
    );
  }

  getUpcomingRenewals(
    days: number = 30,
    contractStatus?: string
  ): Observable<RenewalReportItem[]> {
    let params = new HttpParams().set('days', days.toString());

    if (contractStatus) {
      params = params.set('contract_status', contractStatus);
    }

    return this.http.get<RenewalReportItem[]>(
      `${this.apiUrl}/renewals/upcoming`,
      { params }
    );
  }

  getExpiredRenewals(
    contractStatus?: string
  ): Observable<RenewalReportItem[]> {
    let params = new HttpParams();

    if (contractStatus) {
      params = params.set('contract_status', contractStatus);
    }

    return this.http.get<RenewalReportItem[]>(
      `${this.apiUrl}/renewals/expired`,
      { params }
    );
  }

  getRenewalsRequiringAttention(
    days: number = 30
  ): Observable<RenewalReportItem[]> {
    const params = new HttpParams().set(
      'days',
      days.toString()
    );

    return this.http.get<RenewalReportItem[]>(
      `${this.apiUrl}/renewals/attention`,
      { params }
    );
  }

  getRenewalsByDateRange(
    dateFrom: string,
    dateTo: string
  ): Observable<RenewalReportItem[]> {
    const params = new HttpParams()
      .set('date_from', dateFrom)
      .set('date_to', dateTo);

    return this.http.get<RenewalReportItem[]>(
      `${this.apiUrl}/renewals/date-range`,
      { params }
    );
  }

  getComplianceSummary(
    contractStatus?: string
  ): Observable<ComplianceSummary> {
    let params = new HttpParams();

    if (contractStatus) {
      params = params.set('contract_status', contractStatus);
    }

    return this.http.get<ComplianceSummary>(
      `${this.apiUrl}/compliance/summary`,
      { params }
    );
  }

  getDashboard(): Observable<DashboardReport> {
    return this.http.get<DashboardReport>(
      `${this.apiUrl}/dashboard`
    );
  }
}