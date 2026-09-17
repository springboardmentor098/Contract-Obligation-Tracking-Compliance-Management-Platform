import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

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

export interface RenewalItem {
  contract_id: number;
  contract_number: string;
  expiry_date: string;
  days_remaining: number;
}

export interface RenewalStats {
  upcoming: number;
  in_progress: number;
  renewed: number;
  expired: number;
  cancelled: number;
  approaching_expiry: RenewalItem[];
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

export interface RiskItem {
  contract_id: number;
  contract_number: string;
  risk_level: string;
  overdue_obligations: number;
  compliance_score: number | null;
}

export interface RiskSummary {
  contracts_needing_attention: RiskItem[];
}

@Injectable({
  providedIn: 'root'
})
export class ReportsService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  private buildDateParams(
    startDate?: string,
    endDate?: string
  ): HttpParams {
    let params = new HttpParams();

    if (startDate) {
      params = params.set('start_date', startDate);
    }

    if (endDate) {
      params = params.set('end_date', endDate);
    }

    return params;
  }

  getContractStats(
    startDate?: string,
    endDate?: string,
    status?: string,
    category?: string
  ): Observable<ContractStats> {

    let params = this.buildDateParams(startDate, endDate);

    if (status) {
      params = params.set('status', status);
    }

    if (category) {
      params = params.set('category', category);
    }

    return this.http.get<ContractStats>(
      `${this.apiUrl}/reports/contracts/summary`,
      { params }
    );
  }

  getObligationStats(
    startDate?: string,
    endDate?: string
  ): Observable<ObligationStats> {

    return this.http.get<ObligationStats>(
      `${this.apiUrl}/reports/obligations/summary`,
      {
        params: this.buildDateParams(startDate, endDate)
      }
    );
  }

  getRenewalStats(
    startDate?: string,
    endDate?: string
  ): Observable<RenewalStats> {

    return this.http.get<RenewalStats>(
      `${this.apiUrl}/reports/renewals/summary`,
      {
        params: this.buildDateParams(startDate, endDate)
      }
    );
  }

  getComplianceStats(
    startDate?: string,
    endDate?: string
  ): Observable<ComplianceStats> {

    return this.http.get<ComplianceStats>(
      `${this.apiUrl}/reports/compliance/summary`,
      {
        params: this.buildDateParams(startDate, endDate)
      }
    );
  }

  getRiskSummary(): Observable<RiskSummary> {
    return this.http.get<RiskSummary>(
      `${this.apiUrl}/reports/risk`
    );
  }

  exportContractsPdf(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/contracts/export/pdf`,
      { responseType: 'blob' }
    );
  }

  exportContractsExcel(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/contracts/export/excel`,
      { responseType: 'blob' }
    );
  }

  exportObligationsPdf(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/obligations/export/pdf`,
      { responseType: 'blob' }
    );
  }

  exportObligationsExcel(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/obligations/export/excel`,
      { responseType: 'blob' }
    );
  }

  exportRenewalsPdf(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/renewals/export/pdf`,
      { responseType: 'blob' }
    );
  }

  exportRenewalsExcel(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/renewals/export/excel`,
      { responseType: 'blob' }
    );
  }

  exportCompliancePdf(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/compliance/export/pdf`,
      { responseType: 'blob' }
    );
  }

  exportComplianceExcel(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/reports/compliance/export/excel`,
      { responseType: 'blob' }
    );
  }
}
