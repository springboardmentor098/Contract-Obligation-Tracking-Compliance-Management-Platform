import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

export interface Obligation {
  id: number;
  contract_id: number;
  title: string;
  description: string | null;
  due_date: string;
  priority: string;
  responsible_party: string | null;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface ObligationCreate {
  contract_id: number;
  title: string;
  description?: string | null;
  due_date: string;
  priority: string;
  responsible_party?: string | null;
}

export interface ObligationUpdate {
  title?: string;
  description?: string | null;
  due_date?: string;
  priority?: string;
  responsible_party?: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class ObligationService {

  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  getObligations(): Observable<Obligation[]> {
    return this.http.get<Obligation[]>(
      `${this.apiUrl}/obligations`
    );
  }

  getObligation(id: number): Observable<Obligation> {
    return this.http.get<Obligation>(
      `${this.apiUrl}/obligations/${id}`
    );
  }

  createObligation(
    payload: ObligationCreate
  ): Observable<Obligation> {
    return this.http.post<Obligation>(
      `${this.apiUrl}/obligations`,
      payload
    );
  }

  updateObligation(
    id: number,
    payload: ObligationUpdate
  ): Observable<Obligation> {
    return this.http.put<Obligation>(
      `${this.apiUrl}/obligations/${id}`,
      payload
    );
  }

  updateStatus(
    id: number,
    status: string
  ): Observable<Obligation> {
    return this.http.patch<Obligation>(
      `${this.apiUrl}/obligations/${id}/status`,
      {
        status
      }
    );
  }

  deleteObligation(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/obligations/${id}`
    );
  }

  scanOverdue(): Observable<{
    message: string;
    updated_count: number;
  }> {
    return this.http.post<{
      message: string;
      updated_count: number;
    }>(
      `${this.apiUrl}/obligations/scan-overdue`,
      {}
    );
  }
}
