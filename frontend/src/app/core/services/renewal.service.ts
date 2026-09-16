import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Renewal {
  id: number;
  contract_id: number;
  renewal_date: string;
  status: string;
  renewal_terms: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface RenewalCreate {
  renewal_date: string;
  status: string;
  renewal_terms?: string | null;
}

export interface RenewalUpdate {
  renewal_date?: string;
  status?: string;
  renewal_terms?: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class RenewalService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  getContractRenewals(contractId: number): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      `${this.apiUrl}/contracts/${contractId}/renewals`
    );
  }

  getRenewal(id: number): Observable<Renewal> {
    return this.http.get<Renewal>(
      `${this.apiUrl}/contracts/renewals/${id}`
    );
  }

  createRenewal(
    contractId: number,
    payload: RenewalCreate
  ): Observable<Renewal> {
    return this.http.post<Renewal>(
      `${this.apiUrl}/contracts/${contractId}/renewals`,
      payload
    );
  }

  updateRenewal(
    id: number,
    payload: RenewalUpdate
  ): Observable<Renewal> {
    return this.http.put<Renewal>(
      `${this.apiUrl}/contracts/renewals/${id}`,
      payload
    );
  }

  deleteRenewal(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/contracts/renewals/${id}`
    );
  }
}
