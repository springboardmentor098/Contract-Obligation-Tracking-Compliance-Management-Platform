import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Obligation {
  id: number;
  contract_id: number;
  title: string;
  description: string | null;
  obligation_type: string;
  due_date: string;
  assigned_to: number;
  status: string;
  completion_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface ObligationCreate {
  title: string;
  description?: string;
  obligation_type: string;
  due_date: string;
  assigned_to: number;
  contract_id: number;
}

export interface ObligationUpdate {
  title?: string;
  description?: string;
  obligation_type?: string;
  due_date?: string;
  assigned_to?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ObligationsService {

  private apiUrl = 'http://127.0.0.1:8000/obligations';

  constructor(private http: HttpClient) {}

  getObligations(): Observable<Obligation[]> {
    return this.http.get<Obligation[]>(this.apiUrl);
  }

  getObligation(id: number): Observable<Obligation> {
    return this.http.get<Obligation>(`${this.apiUrl}/${id}`);
  }

  createObligation(
    obligation: ObligationCreate
  ): Observable<Obligation> {
    return this.http.post<Obligation>(
      this.apiUrl,
      obligation
    );
  }

  updateObligation(
    id: number,
    obligation: ObligationUpdate
  ): Observable<Obligation> {
    return this.http.put<Obligation>(
      `${this.apiUrl}/${id}`,
      obligation
    );
  }

  updateStatus(
    id: number,
    status: string
  ): Observable<Obligation> {
    return this.http.patch<Obligation>(
      `${this.apiUrl}/${id}/status`,
      { status }
    );
  }

  completeObligation(id: number): Observable<Obligation> {
    return this.http.post<Obligation>(
      `${this.apiUrl}/${id}/complete`,
      {}
    );
  }
}
