import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Renewal {
  id: number;
  contract_id: number;
  renewal_date: string;
  previous_expiry_date: string | null;
  new_expiry_date: string | null;
  renewal_status: string;
  assigned_to: number | null;
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface RenewalCreate {
  contract_id: number;
  renewal_date: string;
  previous_expiry_date: string;
  new_expiry_date: string;
  assigned_to?: number;
  notes?: string;
}

export interface RenewalUpdate {
  renewal_date?: string;
  new_expiry_date?: string;
  assigned_to?: number;
  notes?: string;
}

@Injectable({
  providedIn: 'root'
})
export class RenewalsService {

  private apiUrl = 'http://127.0.0.1:8000/renewals';

  constructor(private http: HttpClient) {}

  getRenewals(): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(this.apiUrl);
  }

  getRenewal(id: number): Observable<Renewal> {
    return this.http.get<Renewal>(`${this.apiUrl}/${id}`);
  }

  getContractRenewals(
    contractId: number
  ): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      `http://127.0.0.1:8000/contracts/${contractId}/renewals`
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
    id: number,
    renewal: RenewalUpdate
  ): Observable<Renewal> {
    return this.http.put<Renewal>(
      `${this.apiUrl}/${id}`,
      renewal
    );
  }

  updateStatus(
    id: number,
    renewalStatus: string
  ): Observable<Renewal> {
    return this.http.patch<Renewal>(
      `${this.apiUrl}/${id}/status`,
      { renewal_status: renewalStatus }
    );
  }

  renewContract(id: number): Observable<Renewal> {
    return this.http.post<Renewal>(
      `${this.apiUrl}/${id}/renew`,
      {}
    );
  }
}
