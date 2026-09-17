import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  Renewal,
  CreateRenewalRequest,
  UpdateRenewalRequest,
  UpdateRenewalStatusRequest
} from '../models/renewal.model';

@Injectable({
  providedIn: 'root'
})
export class RenewalService {

  private readonly apiUrl =
    'http://127.0.0.1:8000/renewals';

  constructor(
    private readonly http: HttpClient
  ) {}

  getRenewals(): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      this.apiUrl
    );
  }

  getRenewal(
    id: number
  ): Observable<Renewal> {
    return this.http.get<Renewal>(
      `${this.apiUrl}/${id}`
    );
  }

  createRenewal(
    data: CreateRenewalRequest
  ): Observable<Renewal> {
    return this.http.post<Renewal>(
      this.apiUrl,
      data
    );
  }

  updateRenewal(
    id: number,
    data: UpdateRenewalRequest
  ): Observable<Renewal> {
    return this.http.put<Renewal>(
      `${this.apiUrl}/${id}`,
      data
    );
  }

  deleteRenewal(
    id: number
  ): Observable<unknown> {
    return this.http.delete(
      `${this.apiUrl}/${id}`
    );
  }

  getContractRenewals(
    contractId: number
  ): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      `${this.apiUrl}/contract/${contractId}`
    );
  }

  updateStatus(
    id: number,
    data: UpdateRenewalStatusRequest
  ): Observable<Renewal> {
    return this.http.patch<Renewal>(
      `${this.apiUrl}/${id}/status`,
      data
    );
  }

  renew(
    id: number
  ): Observable<Renewal> {
    return this.http.post<Renewal>(
      `${this.apiUrl}/${id}/renew`,
      {}
    );
  }

  getUpcomingRenewals(): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      `${this.apiUrl}/upcoming`
    );
  }

  getExpiredRenewals(): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(
      `${this.apiUrl}/expired`
    );
  }
}