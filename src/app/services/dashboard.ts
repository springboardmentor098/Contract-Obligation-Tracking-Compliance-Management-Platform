import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  private apiUrl = 'http://127.0.0.1:8000/reports/dashboard';

  constructor(private http: HttpClient) {}

  getDashboardSummary() {
    return this.http.get<any>(
      `${this.apiUrl}/summary`
    );
  }
}