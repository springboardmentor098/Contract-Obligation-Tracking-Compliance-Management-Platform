import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ReportService {

  private apiUrl = 'http://127.0.0.1:8000/reports';

  constructor(private http: HttpClient) {}

  // =====================================================
  // CONTRACT REPORT
  // =====================================================

  getContractsReport() {
    return this.http.get<any[]>(
      `${this.apiUrl}/contracts/report`
    );
  }

  // =====================================================
  // OBLIGATION REPORT
  // =====================================================

  getObligationsReport() {
    return this.http.get<any[]>(
      `${this.apiUrl}/obligations/report`
    );
  }

  // =====================================================
  // RENEWAL REPORT
  // =====================================================

  getRenewalsReport() {
    return this.http.get<any[]>(
      `${this.apiUrl}/renewals/report`
    );
  }

  // =====================================================
  // COMPLIANCE REPORT
  // =====================================================

  getComplianceReport() {
    return this.http.get<any[]>(
      `${this.apiUrl}/compliance/report`
    );
  }

  // =====================================================
  // EXCEL DOWNLOADS
  // =====================================================

  downloadContractsExcel() {
    return this.http.get(
      `${this.apiUrl}/contracts/excel`,
      {
        responseType: 'blob'
      }
    );
  }

  downloadObligationsExcel() {
    return this.http.get(
      `${this.apiUrl}/obligations/excel`,
      {
        responseType: 'blob'
      }
    );
  }

  downloadRenewalsExcel() {
    return this.http.get(
      `${this.apiUrl}/renewals/excel`,
      {
        responseType: 'blob'
      }
    );
  }

  downloadComplianceExcel() {
    return this.http.get(
      `${this.apiUrl}/compliance/excel`,
      {
        responseType: 'blob'
      }
    );
  }
}
