import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Renewal {
  id: string;
  contract_id: string;
  renewal_date: string | null;
  previous_expiry_date: string | null;
  new_expiry_date: string | null;
  status: string;
  assigned_to: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface RenewalCreate {
  contract_id: string;
  renewal_date?: string | null;
  previous_expiry_date?: string | null;
  new_expiry_date?: string | null;
  assigned_to: string;
  notes?: string | null;
}

export interface RenewalUpdate {
  renewal_date?: string | null;
  previous_expiry_date?: string | null;
  new_expiry_date?: string | null;
  assigned_to?: string | null;
  notes?: string | null;
}

export interface RenewalStatusUpdate {
  status: string;
}

export interface RenewalComplete {
  new_expiry_date: string;
}

@Injectable({
  providedIn: 'root'
})
export class RenewalService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    'http://127.0.0.1:8000/renewals';

  getRenewals(): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      this.apiUrl
    );
  }

  getRenewal(id: string): Observable<Renewal> {
    return this.http.get<Renewal>(
      `${this.apiUrl}/${id}`
    );
  }

  createRenewal(
    renewal: RenewalCreate
  ): Observable<Renewal> {
    return this.http.post<Renewal>(
      this.apiUrl,
      renewal
    );
  }

  updateRenewal(
    id: string,
    renewal: RenewalUpdate
  ): Observable<Renewal> {
    return this.http.put<Renewal>(
      `${this.apiUrl}/${id}`,
      renewal
    );
  }

  updateStatus(
    id: string,
    status: string
  ): Observable<Renewal> {
    const data: RenewalStatusUpdate = {
      status
    };

    return this.http.patch<Renewal>(
      `${this.apiUrl}/${id}/status`,
      data
    );
  }

  completeRenewal(
    id: string,
    newExpiryDate: string
  ): Observable<Renewal> {
    const data: RenewalComplete = {
      new_expiry_date: newExpiryDate
    };

    return this.http.post<Renewal>(
      `${this.apiUrl}/${id}/renew`,
      data
    );
  }

  getUpcomingRenewals(
    days: number = 90
  ): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      `${this.apiUrl}/upcoming/list`,
      {
        params: {
          days: days.toString()
        }
      }
    );
  }

  getExpiredRenewals(): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      `${this.apiUrl}/expired/list`
    );
  }

  getContractRenewals(
    contractId: string
  ): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      `${this.apiUrl}/contracts/${contractId}/renewals`
    );
  }

  deleteRenewal(id: string): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/${id}`
    );
  }
}