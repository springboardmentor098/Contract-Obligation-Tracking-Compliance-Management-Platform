import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


export interface DashboardSummary {

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

    overdue: number;

  };


  renewals: {

    upcoming: number;

    in_progress: number;

    renewed: number;

    expired: number;

  };


  compliance: {

    compliant: number;

    pending: number;

    delayed: number;

    non_compliant: number;

    high_risk: number;

  };

}


export interface ContractSummary {

  total: number;

  active: number;

  draft: number;

  under_review: number;

  approved: number;

  expired: number;

  terminated: number;

  contracts_by_category: Record<string, number>;

}


export interface ObligationSummary {

  total: number;

  pending: number;

  in_progress: number;

  completed: number;

  delayed: number;

  overdue: number;

}


export interface RenewalSummary {

  upcoming: number;

  in_progress: number;

  renewed: number;

  expired: number;

  cancelled: number;

  approaching_expiry: unknown[];

}


export interface ComplianceSummary {

  total_evaluated: number;

  compliant: number;

  pending: number;

  delayed: number;

  non_compliant: number;

  high_risk: number;

  average_score: number;

}


@Injectable({
  providedIn: 'root'
})
export class Dashboard {

  private readonly baseUrl =
    'http://127.0.0.1:8000';


  constructor(
    private http: HttpClient
  ) {}


  getDashboardSummary(): Observable<DashboardSummary> {

    return this.http.get<DashboardSummary>(
      `${this.baseUrl}/dashboard/summary`
    );

  }


  getContractSummary(): Observable<ContractSummary> {

    return this.http.get<ContractSummary>(
      `${this.baseUrl}/reports/contracts/summary`
    );

  }


  getObligationSummary(): Observable<ObligationSummary> {

    return this.http.get<ObligationSummary>(
      `${this.baseUrl}/reports/obligations/summary`
    );

  }


  getRenewalSummary(): Observable<RenewalSummary> {

    return this.http.get<RenewalSummary>(
      `${this.baseUrl}/reports/renewals/summary`
    );

  }


  getComplianceSummary(): Observable<ComplianceSummary> {

    return this.http.get<ComplianceSummary>(
      `${this.baseUrl}/reports/compliance/summary`
    );

  }

}