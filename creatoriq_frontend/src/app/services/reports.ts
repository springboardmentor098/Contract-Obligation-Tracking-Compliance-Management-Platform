import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ContractReportItem {
  contract_number: string;
  title: string;
  category: string;
  status: string;
  start_date: string | null;
  end_date: string | null;
  assigned_user: string | null;
}

export interface ContractReport {
  report_type: string;
  total_records: number;
  data: ContractReportItem[];
}

export interface ObligationReportItem {
  contract_number: string;
  title: string;
  obligation_type: string;
  assigned_user: string | null;
  due_date: string | null;
  status: string;
  completion_date: string | null;
}

export interface ObligationReport {
  report_type: string;
  total_records: number;
  data: ObligationReportItem[];
}

export interface RenewalReportItem {
  contract_number: string;
  previous_expiry_date: string | null;
  renewal_date: string | null;
  new_expiry_date: string | null;
  status: string;
  assigned_user: string | null;
}

export interface RenewalReport {
  report_type: string;
  total_records: number;
  data: RenewalReportItem[];
}

export interface ComplianceReportItem {
  contract_number: string;
  compliance_status: string;
  compliance_score: number;
  overdue_obligations: number;
  risk_level: string;
  evaluation_date: string;
}

export interface ComplianceReport {
  report_type: string;
  total_records: number;
  data: ComplianceReportItem[];
}

@Injectable({
  providedIn: 'root'
})
export class Reports {

  private readonly baseUrl = 'http://127.0.0.1:8000/reports';

  constructor(private http: HttpClient) {}

  getContractReport(status?: string): Observable<ContractReport> {
    let params = new HttpParams();

    if (status) {
      params = params.set('status', status);
    }

    return this.http.get<ContractReport>(
      `${this.baseUrl}/contracts`,
      { params }
    );
  }

  getObligationReport(status?: string): Observable<ObligationReport> {
    let params = new HttpParams();

    if (status) {
      params = params.set('status', status);
    }

    return this.http.get<ObligationReport>(
      `${this.baseUrl}/obligations`,
      { params }
    );
  }

  getRenewalReport(
    status?: string,
    startDate?: string,
    endDate?: string
  ): Observable<RenewalReport> {

    let params = new HttpParams();

    if (status) {
      params = params.set('status', status);
    }

    if (startDate) {
      params = params.set('start_date', startDate);
    }

    if (endDate) {
      params = params.set('end_date', endDate);
    }

    return this.http.get<RenewalReport>(
      `${this.baseUrl}/renewals`,
      { params }
    );
  }

  getComplianceReport(): Observable<ComplianceReport> {
    return this.http.get<ComplianceReport>(
      `${this.baseUrl}/compliance`
    );
  }

  downloadContractPdf(): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/contracts/pdf`,
      { responseType: 'blob' }
    );
  }

  downloadContractExcel(): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/contracts/excel`,
      { responseType: 'blob' }
    );
  }

  downloadObligationPdf(): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/obligations/pdf`,
      { responseType: 'blob' }
    );
  }

  downloadObligationExcel(): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/obligations/excel`,
      { responseType: 'blob' }
    );
  }

  downloadRenewalPdf(): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/renewals/pdf`,
      { responseType: 'blob' }
    );
  }

  downloadRenewalExcel(): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/renewals/excel`,
      { responseType: 'blob' }
    );
  }

  downloadCompliancePdf(): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/compliance/pdf`,
      { responseType: 'blob' }
    );
  }

  downloadComplianceExcel(): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/compliance/excel`,
      { responseType: 'blob' }
    );
  }
}