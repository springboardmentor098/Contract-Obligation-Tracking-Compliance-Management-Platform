import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


// =====================================================
// CONTRACT SUMMARY
// =====================================================

export interface ContractSummary {
  total_contracts: number;
  active_contracts: number;
  expired_contracts: number;
  pending_approval_contracts: number;

  contracts_by_status: {
    [key: string]: number;
  };

  contracts_by_category: {
    [key: string]: number;
  };
}


// =====================================================
// OBLIGATION SUMMARY
// =====================================================

export interface ObligationSummary {
  total_obligations: number;
  pending_obligations: number;
  completed_obligations: number;
  overdue_obligations: number;
  in_progress_obligations: number;
  delayed_obligations: number;

  obligations_by_status: {
    [key: string]: number;
  };
}


// =====================================================
// UPCOMING RENEWAL
// =====================================================

export interface UpcomingRenewal {
  contract_id: number;
  contract_number: string;
  expiry_date: string;
  days_remaining: number;
}


// =====================================================
// RENEWAL SUMMARY
// =====================================================

export interface RenewalSummary {
  upcoming: number;
  in_progress: number;
  renewed: number;
  expired: number;
  cancelled: number;

  upcoming_contracts: UpcomingRenewal[];

  immediate_attention: UpcomingRenewal[];

  renewals_in_date_range: number;
}


// =====================================================
// COMPLIANCE SUMMARY
// =====================================================

export interface ComplianceSummary {
  total_contracts: number;
  compliant: number;
  pending: number;
  delayed: number;
  non_compliant: number;
  high_risk: number;
  average_score: number;
}


// =====================================================
// RISK REPORT
// =====================================================

export interface RiskSummary {
  contract_id: number;
  contract_number: string;
  risk_level: string;
  overdue_obligations: number;
  compliance_score: number;
}


// =====================================================
// REPORT SERVICE
// =====================================================

@Injectable({
  providedIn: 'root'
})
export class ReportService {

  private apiUrl = 'http://127.0.0.1:8000';


  constructor(
    private http: HttpClient
  ) {}


  // =====================================================
  // CONTRACT REPORT
  // GET /reports/contracts/summary
  // =====================================================

  getContractSummary(): Observable<ContractSummary> {

    return this.http.get<ContractSummary>(
      `${this.apiUrl}/reports/contracts/summary`
    );

  }


  // =====================================================
  // OBLIGATION REPORT
  // GET /reports/obligations/summary
  // =====================================================

  getObligationSummary(): Observable<ObligationSummary> {

    return this.http.get<ObligationSummary>(
      `${this.apiUrl}/reports/obligations/summary`
    );

  }


  // =====================================================
  // RENEWAL REPORT
  // GET /reports/renewals/summary
  // =====================================================

  getRenewalSummary(): Observable<RenewalSummary> {

    return this.http.get<RenewalSummary>(
      `${this.apiUrl}/reports/renewals/summary`
    );

  }


  // =====================================================
  // COMPLIANCE REPORT
  // GET /reports/compliance/summary
  // =====================================================

  getComplianceSummary(): Observable<ComplianceSummary> {

    return this.http.get<ComplianceSummary>(
      `${this.apiUrl}/reports/compliance/summary`
    );

  }


  // =====================================================
  // RISK REPORT
  // GET /reports/risk
  // =====================================================

  getRiskReport(): Observable<RiskSummary[]> {

    return this.http.get<RiskSummary[]>(
      `${this.apiUrl}/reports/risk`
    );

  }


  // =====================================================
  // CONTRACT PDF
  // GET /reports/contracts/export/pdf
  // =====================================================

  downloadContractPdf(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/reports/contracts/export/pdf`,
      {
        responseType: 'blob'
      }
    );

  }


  // =====================================================
  // CONTRACT EXCEL
  // GET /reports/contracts/export/excel
  // =====================================================

  downloadContractExcel(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/reports/contracts/export/excel`,
      {
        responseType: 'blob'
      }
    );

  }


  // =====================================================
  // OBLIGATION PDF
  // GET /reports/obligations/export/pdf
  // =====================================================

  downloadObligationPdf(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/reports/obligations/export/pdf`,
      {
        responseType: 'blob'
      }
    );

  }


  // =====================================================
  // OBLIGATION EXCEL
  // GET /reports/obligations/export/excel
  // =====================================================

  downloadObligationExcel(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/reports/obligations/export/excel`,
      {
        responseType: 'blob'
      }
    );

  }


  // =====================================================
  // RENEWAL PDF
  // GET /reports/renewals/export/pdf
  // =====================================================

  downloadRenewalPdf(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/reports/renewals/export/pdf`,
      {
        responseType: 'blob'
      }
    );

  }


  // =====================================================
  // RENEWAL EXCEL
  // GET /reports/renewals/export/excel
  // =====================================================

  downloadRenewalExcel(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/reports/renewals/export/excel`,
      {
        responseType: 'blob'
      }
    );

  }


  // =====================================================
  // COMPLIANCE PDF
  // GET /reports/compliance/export/pdf
  // =====================================================

  downloadCompliancePdf(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/reports/compliance/export/pdf`,
      {
        responseType: 'blob'
      }
    );

  }


  // =====================================================
  // COMPLIANCE EXCEL
  // GET /reports/compliance/export/excel
  // =====================================================

  downloadComplianceExcel(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/reports/compliance/export/excel`,
      {
        responseType: 'blob'
      }
    );

  }

}