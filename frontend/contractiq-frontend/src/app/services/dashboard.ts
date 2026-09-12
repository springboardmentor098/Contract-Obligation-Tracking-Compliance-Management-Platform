import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


// =====================================================
// DASHBOARD SUMMARY
// =====================================================

export interface DashboardData {
  contracts: {
    total: number;
    active: number;
    draft: number;
    under_review: number;
    approved: number;
    expired: number;
    terminated: number;
  };

  obligations: {
    total: number;
    pending: number;
    in_progress: number;
    completed: number;
    delayed: number;
    overdue: number;
  };

  renewals: {
    upcoming: number;
    in_progress: number;
    renewed: number;
    expired: number;
    cancelled: number;
  };

  compliance: {
    total: number;
    compliant: number;
    pending: number;
    delayed: number;
    non_compliant: number;
    high_risk: number;
    average_score: number;
  };
}


// =====================================================
// CONTRACT REPORT
// =====================================================

export interface ContractReport {
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
// DASHBOARD SERVICE
// =====================================================

@Injectable({
  providedIn: 'root'
})
export class Dashboard {

  private apiUrl = 'http://127.0.0.1:8000';


  constructor(
    private http: HttpClient
  ) {}


  // ===================================================
  // DASHBOARD SUMMARY
  // GET /dashboard/summary
  // ===================================================

  getDashboardSummary(): Observable<DashboardData> {

    return this.http.get<DashboardData>(
      `${this.apiUrl}/dashboard/summary`
    );

  }


  // ===================================================
  // CONTRACT REPORT
  // GET /reports/contracts/summary
  // ===================================================

  getContractSummary(): Observable<ContractReport> {

    return this.http.get<ContractReport>(
      `${this.apiUrl}/reports/contracts/summary`
    );

  }

}