import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ReportService {

  private readonly apiUrl =
    'http://127.0.0.1:8000/reports';

  constructor(
    private readonly http: HttpClient
  ) {}

  // =========================================================
  // HELPER
  // =========================================================

  private extractRows(response: unknown): any[] {

    // Case 1:
    // Backend/interceptor already returned an array
    if (Array.isArray(response)) {
      return response;
    }

    // Case 2:
    // Backend returned:
    // { value: [...], Count: 6 }
    if (
      response !== null &&
      typeof response === 'object'
    ) {
      const data = response as {
        value?: unknown;
        data?: unknown;
      };

      if (Array.isArray(data.value)) {
        return data.value;
      }

      if (Array.isArray(data.data)) {
        return data.data;
      }
    }

    return [];
  }

  // =========================================================
  // CONTRACT REPORT
  // =========================================================

  getContractsReport(): Observable<any[]> {

    return this.http
      .get<unknown>(
        `${this.apiUrl}/contracts/report`
      )
      .pipe(
        map(response => {
          console.log(
            'Contract Report raw response:',
            response
          );

          const rows =
            this.extractRows(response);

          console.log(
            'Contract Report rows:',
            rows
          );

          return rows;
        })
      );
  }

  // =========================================================
  // OBLIGATION REPORT
  // =========================================================

  getObligationsReport(): Observable<any[]> {

    return this.http
      .get<unknown>(
        `${this.apiUrl}/obligations/report`
      )
      .pipe(
        map(response => {
          console.log(
            'Obligation Report raw response:',
            response
          );

          const rows =
            this.extractRows(response);

          console.log(
            'Obligation Report rows:',
            rows
          );

          return rows;
        })
      );
  }

  // =========================================================
  // RENEWAL REPORT
  // =========================================================

  getRenewalsReport(): Observable<any[]> {

    return this.http
      .get<unknown>(
        `${this.apiUrl}/renewals/report`
      )
      .pipe(
        map(response => {
          console.log(
            'Renewal Report raw response:',
            response
          );

          const rows =
            this.extractRows(response);

          console.log(
            'Renewal Report rows:',
            rows
          );

          return rows;
        })
      );
  }

  // =========================================================
  // COMPLIANCE REPORT
  // =========================================================

  getComplianceReport(): Observable<any[]> {

    return this.http
      .get<unknown>(
        `${this.apiUrl}/compliance/report`
      )
      .pipe(
        map(response => {
          console.log(
            'Compliance Report raw response:',
            response
          );

          const rows =
            this.extractRows(response);

          console.log(
            'Compliance Report rows:',
            rows
          );

          return rows;
        })
      );
  }

  // =========================================================
  // EXCEL DOWNLOADS
  // =========================================================

  downloadContractsExcel(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/contracts/excel`,
      {
        responseType: 'blob'
      }
    );
  }

  downloadObligationsExcel(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/obligations/excel`,
      {
        responseType: 'blob'
      }
    );
  }

  downloadRenewalsExcel(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/renewals/excel`,
      {
        responseType: 'blob'
      }
    );
  }

  downloadComplianceExcel(): Observable<Blob> {

    return this.http.get(
      `${this.apiUrl}/compliance/excel`,
      {
        responseType: 'blob'
      }
    );
  }
}