import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}


  // ==============================
  // COMMON AUTHENTICATION HEADERS
  // ==============================

  private getHeaders(): HttpHeaders {

    const token = localStorage.getItem('access_token');

    console.log('Token:', token);

    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }


  // ==============================
  // DASHBOARD SUMMARY
  // ==============================

  getDashboardSummary() {

    return this.http.get<any>(
      `${this.apiUrl}/dashboard/summary`,
      {
        headers: this.getHeaders()
      }
    );
  }


  // ==============================
  // CONTRACT SUMMARY
  // ==============================

  getContractSummary() {

    return this.http.get<any>(
      `${this.apiUrl}/reports/contracts/summary`,
      {
        headers: this.getHeaders()
      }
    );
  }


  // ==============================
  // OBLIGATION SUMMARY
  // ==============================

  getObligationSummary() {

    return this.http.get<any>(
      `${this.apiUrl}/reports/obligations/summary`,
      {
        headers: this.getHeaders()
      }
    );
  }


  // ==============================
  // RENEWAL SUMMARY
  // ==============================

  getRenewalSummary() {

    return this.http.get<any>(
      `${this.apiUrl}/reports/renewals/summary`,
      {
        headers: this.getHeaders()
      }
    );
  }


  // ==============================
  // COMPLIANCE SUMMARY
  // ==============================

  getComplianceSummary() {

    return this.http.get<any>(
      `${this.apiUrl}/reports/compliance/summary`,
      {
        headers: this.getHeaders()
      }
    );
  }


  // ==============================
  // RISK REPORT
  // ==============================

  getRiskReport() {

    return this.http.get<any>(
      `${this.apiUrl}/reports/risk`,
      {
        headers: this.getHeaders()
      }
    );
  }


  // ==============================
  // UPCOMING EXPIRY CONTRACTS
  // ==============================

  getUpcomingExpiry() {

    return this.http.get<any>(
      `${this.apiUrl}/reports/contracts/upcoming-expiry`,
      {
        headers: this.getHeaders()
      }
    );
  }


  // ==============================
  // DEPARTMENT PERFORMANCE
  // ==============================

  getDepartmentPerformance() {

    return this.http.get<any>(
      `${this.apiUrl}/reports/departments/performance`,
      {
        headers: this.getHeaders()
      }
    );
  }
// ==============================
// UPCOMING RENEWALS
// ==============================

getUpcomingRenewals() {

  return this.http.get<any>(
    `${this.apiUrl}/reports/renewals/upcoming`,
    {
      headers: this.getHeaders()
    }
  );

}
// ===============================
// DOWNLOAD CONTRACT PDF
// ===============================

downloadContractPdf() {

  return this.http.get(
    `${this.apiUrl}/reports/contracts/export/pdf`,
    {
      headers: this.getHeaders(),
      responseType: 'blob'
    }
  );
}


// ===============================
// DOWNLOAD CONTRACT EXCEL
// ===============================

downloadContractExcel() {

  return this.http.get(
    `${this.apiUrl}/reports/contracts/export/excel`,
    {
      headers: this.getHeaders(),
      responseType: 'blob'
    }
  );
}


// ===============================
// DOWNLOAD OBLIGATION PDF
// ===============================

downloadObligationPdf() {

  return this.http.get(
    `${this.apiUrl}/reports/obligations/export/pdf`,
    {
      headers: this.getHeaders(),
      responseType: 'blob'
    }
  );
}


// ===============================
// DOWNLOAD OBLIGATION EXCEL
// ===============================

downloadObligationExcel() {

  return this.http.get(
    `${this.apiUrl}/reports/obligations/export/excel`,
    {
      headers: this.getHeaders(),
      responseType: 'blob'
    }
  );
}


// ===============================
// DOWNLOAD RENEWAL PDF
// ===============================

downloadRenewalPdf() {

  return this.http.get(
    `${this.apiUrl}/reports/renewals/export/pdf`,
    {
      headers: this.getHeaders(),
      responseType: 'blob'
    }
  );
}


// ===============================
// DOWNLOAD RENEWAL EXCEL
// ===============================

downloadRenewalExcel() {

  return this.http.get(
    `${this.apiUrl}/reports/renewals/export/excel`,
    {
      headers: this.getHeaders(),
      responseType: 'blob'
    }
  );
}


// ===============================
// DOWNLOAD COMPLIANCE PDF
// ===============================

downloadCompliancePdf() {

  return this.http.get(
    `${this.apiUrl}/reports/compliance/export/pdf`,
    {
      headers: this.getHeaders(),
      responseType: 'blob'
    }
  );
}


// ===============================
// DOWNLOAD COMPLIANCE EXCEL
// ===============================

downloadComplianceExcel() {

  return this.http.get(
    `${this.apiUrl}/reports/compliance/export/excel`,
    {
      headers: this.getHeaders(),
      responseType: 'blob'
    }
  );
}
// ===============================
// OVERDUE OBLIGATIONS
// ===============================

getOverdueObligations() {

  return this.http.get<any>(
    `${this.apiUrl}/reports/obligations/overdue`,
    {
      headers: this.getHeaders()
    }
  );

}
}
