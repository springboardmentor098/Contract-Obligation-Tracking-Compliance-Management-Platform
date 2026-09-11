import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class Api {
  private http = inject(HttpClient);
  private auth = inject(AuthService);

  private readonly baseUrl = 'http://127.0.0.1:8000';

  private headers(): HttpHeaders {
    const token = this.auth.getToken();

    let headers = new HttpHeaders({
      'Accept': 'application/json'
    });

    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }

    return headers;
  }

  getDashboardSummary(): Observable<any> {
    return this.http.get(
      `${this.baseUrl}/dashboard/summary`,
      { headers: this.headers() }
    );
  }

  getContractSummary(): Observable<any> {
    return this.http.get(
      `${this.baseUrl}/reports/contracts/summary`,
      { headers: this.headers() }
    );
  }

  getObligationSummary(): Observable<any> {
    return this.http.get(
      `${this.baseUrl}/reports/obligations/summary`,
      { headers: this.headers() }
    );
  }

  getRenewals(): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/renewals`,
      { headers: this.headers() }
    );
  }

  updateRenewalStatus(
    renewalId: number,
    status: string
  ): Observable<any> {
    return this.http.patch(
      `${this.baseUrl}/renewals/${renewalId}/status`,
      { status },
      { headers: this.headers() }
    );
  }

  completeRenewal(
    renewalId: number
  ): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/renewals/${renewalId}/renew`,
      {},
      { headers: this.headers() }
    );
  }

  getRenewalSummary(): Observable<any> {
    return this.http.get(
      `${this.baseUrl}/reports/renewals/summary`,
      { headers: this.headers() }
    );
  }

  getComplianceSummary(): Observable<any> {
    return this.http.get(
      `${this.baseUrl}/reports/compliance/summary`,
      { headers: this.headers() }
    );
  }

  getRiskReport(): Observable<any> {
    return this.http.get(
      `${this.baseUrl}/reports/risk`,
      { headers: this.headers() }
    );
  }

  getNotifications(): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/notifications`,
      { headers: this.headers() }
    );
  }

  markNotificationRead(notificationId: number): Observable<any> {
    return this.http.patch(
      `${this.baseUrl}/notifications/${notificationId}/read`,
      {},
      { headers: this.headers() }
    );
  }

  markAllNotificationsRead(): Observable<any> {
    return this.http.patch(
      `${this.baseUrl}/notifications/read-all`,
      {},
      { headers: this.headers() }
    );
  }

  downloadReport(
    type: string,
    format: 'pdf' | 'excel'
  ): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/reports/${type}/export/${format}`,
      {
        headers: this.headers(),
        responseType: 'blob'
      }
    );
  }
}
