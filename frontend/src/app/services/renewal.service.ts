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

  /**
   * Get all renewals available to the
   * logged-in user.
   */
  getRenewals(): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      this.apiUrl
    );
  }

  /**
   * Get a single renewal by ID.
   */
  getRenewal(id: string): Observable<Renewal> {
    return this.http.get<Renewal>(
      `${this.apiUrl}/${id}`
    );
  }

  /**
   * Create a new renewal.
   */
  createRenewal(
    renewal: RenewalCreate
  ): Observable<Renewal> {
    return this.http.post<Renewal>(
      this.apiUrl,
      renewal
    );
  }

  /**
   * Update an existing renewal.
   */
  updateRenewal(
    id: string,
    renewal: RenewalUpdate
  ): Observable<Renewal> {
    return this.http.put<Renewal>(
      `${this.apiUrl}/${id}`,
      renewal
    );
  }

  /**
   * Update renewal status.
   */
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

  /**
   * Complete a renewal.
   *
   * Backend changes the renewal status to
   * Renewed and updates the contract expiry date.
   */
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

  /**
   * Get renewals coming up within the
   * specified number of days.
   */
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

  /**
   * Get expired renewals.
   */
  getExpiredRenewals(): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      `${this.apiUrl}/expired/list`
    );
  }

  /**
   * Get renewals belonging to a specific contract.
   */
  getContractRenewals(
    contractId: string
  ): Observable<Renewal[]> {

    return this.http.get<Renewal[]>(
      `${this.apiUrl}/contracts/${contractId}/renewals`
    );
  }
}