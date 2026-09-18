import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';
import { Renewal } from '../models/models';


export interface RenewalCreatePayload {
  contract_id: number;
  renewal_date: string;
  previous_expiry_date: string;
  new_expiry_date: string;
  assigned_to?: number;
  notes?: string;
}


export interface RenewalUpdatePayload {
  renewal_date?: string;
  previous_expiry_date?: string;
  new_expiry_date?: string;
  assigned_to?: number;
  notes?: string;
}


export interface RenewalCompletePayload {
  new_expiry_date?: string;
  notes?: string;
}


@Injectable({
  providedIn: 'root'
})
export class RenewalService {

  private readonly api = inject(ApiService);


  // ============================================================
  // GET ALL RENEWALS
  // ============================================================

  list(): Observable<Renewal[]> {
    return this.api.get<Renewal[]>('/renewals');
  }


  // ============================================================
  // GET ONE RENEWAL
  // ============================================================

  get(id: number | string): Observable<Renewal> {
    return this.api.get<Renewal>(
      `/renewals/${id}`
    );
  }


  // ============================================================
  // CREATE
  // POST /renewals
  // ============================================================

  create(
    data: RenewalCreatePayload
  ): Observable<Renewal> {

    return this.api.post<Renewal>(
      '/renewals',
      data
    );
  }


  // ============================================================
  // UPDATE
  // PUT /renewals/{id}
  // ============================================================

  update(
    id: number | string,
    data: RenewalUpdatePayload
  ): Observable<Renewal> {

    return this.api.put<Renewal>(
      `/renewals/${id}`,
      data
    );
  }


  // ============================================================
  // UPDATE STATUS
  // PATCH /renewals/{id}/status
  // ============================================================

  status(
    id: number | string,
    newStatus: string
  ): Observable<Renewal> {

    return this.api.patch<Renewal>(
      `/renewals/${id}/status`,
      {
        status: newStatus
      }
    );
  }


  // ============================================================
  // COMPLETE
  // POST /renewals/{id}/renew
  // ============================================================

  complete(
    id: number | string,
    data?: RenewalCompletePayload
  ): Observable<Renewal> {

    return this.api.post<Renewal>(
      `/renewals/${id}/renew`,
      data ?? {}
    );
  }

}
