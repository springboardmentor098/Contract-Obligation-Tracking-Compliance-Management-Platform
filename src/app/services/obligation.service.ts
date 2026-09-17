import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  Obligation,
  CreateObligationRequest,
  UpdateObligationRequest,
  UpdateObligationStatusRequest
} from '../models/obligation.model';

@Injectable({
  providedIn: 'root'
})
export class ObligationService {
  private readonly apiUrl = 'http://127.0.0.1:8000/obligations';

  constructor(private http: HttpClient) {}

  getObligations(): Observable<Obligation[]> {
    return this.http.get<Obligation[]>(this.apiUrl);
  }

  getObligation(id: number): Observable<Obligation> {
    return this.http.get<Obligation>(`${this.apiUrl}/${id}`);
  }

  getContractObligations(contractId: number): Observable<Obligation[]> {
    return this.http.get<Obligation[]>(
      `${this.apiUrl}/contracts/${contractId}/obligations`
    );
  }

  createObligation(
    data: CreateObligationRequest
  ): Observable<Obligation> {
    return this.http.post<Obligation>(this.apiUrl, data);
  }

  updateObligation(
    id: number,
    data: UpdateObligationRequest
  ): Observable<Obligation> {
    return this.http.put<Obligation>(
      `${this.apiUrl}/${id}`,
      data
    );
  }

  updateStatus(
    id: number,
    data: UpdateObligationStatusRequest
  ): Observable<Obligation> {
    return this.http.patch<Obligation>(
      `${this.apiUrl}/${id}/status`,
      data
    );
  }

  completeObligation(id: number): Observable<Obligation> {
    return this.http.post<Obligation>(
      `${this.apiUrl}/${id}/complete`,
      {}
    );
  }
}