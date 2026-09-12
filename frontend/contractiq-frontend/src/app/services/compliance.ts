import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';


// =========================
// BACKEND RESPONSE
// =========================

interface BackendComplianceSummary {
  total_contracts: number;
  compliant_contracts: number;
  pending_contracts: number;
  delayed_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
}


// =========================
// FRONTEND SUMMARY
// =========================

export interface ComplianceSummary {
  total: number;
  compliant: number;
  pending: number;
  delayed: number;
  non_compliant: number;
  high_risk: number;
  average_score: number;
}


// =========================
// ALL COMPLIANCE RESPONSE
// =========================

export interface ComplianceRecord {
  contract_id: number;
  contract_number: string;
  compliance_status: string;
  compliance_score: number;
}


// =========================
// RISK RESPONSE
// =========================

export interface ComplianceRisk {
  contract_id: number;
  contract_number: string;
  risk_level: string;
  overdue_obligations: number;
  compliance_score: number;
}


// =========================
// SERVICE
// =========================

@Injectable({
  providedIn: 'root'
})
export class ComplianceService {

  private apiUrl = 'http://127.0.0.1:8000';


  constructor(
    private http: HttpClient
  ) {}


  // =========================
  // GET COMPLIANCE SUMMARY
  // =========================

  getComplianceSummary(): Observable<ComplianceSummary> {

    return this.http
      .get<BackendComplianceSummary>(
        `${this.apiUrl}/compliance/summary`
      )
      .pipe(

        map((data) => ({

          total: data.total_contracts,

          compliant: data.compliant_contracts,

          pending: data.pending_contracts,

          delayed: data.delayed_contracts,

          non_compliant: data.non_compliant_contracts,

          high_risk: data.high_risk_contracts,

          // Average score is not provided
          // by /compliance/summary.
          average_score: 0

        }))

      );

  }


  // =========================
  // GET ALL COMPLIANCE
  // =========================

  getAllCompliance(): Observable<ComplianceRecord[]> {

    return this.http.get<ComplianceRecord[]>(
      `${this.apiUrl}/compliance`
    );

  }


  // =========================
  // GET HIGH RISK
  // =========================

  getRiskReport(): Observable<ComplianceRisk[]> {

    return this.http.get<ComplianceRisk[]>(
      `${this.apiUrl}/compliance/high-risk`
    );

  }

}