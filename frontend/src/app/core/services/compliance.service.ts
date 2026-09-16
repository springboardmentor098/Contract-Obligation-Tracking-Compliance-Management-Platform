import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ComplianceData {
  total_contracts: number;
  compliant_contracts: number;
  non_compliant_contracts: number;
  high_risk_contracts: number;
  compliance_rate: number;
  overdue_obligations: number;
  high_priority_overdue_obligations: number;
}

export interface ComplianceResponse {
  compliance: ComplianceData;
}

@Injectable({
  providedIn: 'root'
})
export class ComplianceService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  getCompliance(): Observable<ComplianceResponse> {
    return this.http.get<ComplianceResponse>(
      `${this.apiUrl}/reports/analytics/compliance`
    );
  }
}
