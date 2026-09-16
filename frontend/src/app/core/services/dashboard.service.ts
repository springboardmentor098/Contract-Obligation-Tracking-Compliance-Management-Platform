import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

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
export class DashboardService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl = environment.apiUrl;

  getDashboardSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(
      `${this.apiUrl}/reports/dashboard/summary`
    );
  }
}
