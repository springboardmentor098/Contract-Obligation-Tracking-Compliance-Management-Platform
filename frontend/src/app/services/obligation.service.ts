import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Obligation {
  id: string;
  contract_id: string;
  assigned_to: string;
  title: string;
  description: string | null;
  obligation_type: string | null;
  due_date: string | null;
  status: string | null;
  priority: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ObligationCreate {
  contract_id: string;
  assigned_to: string;
  title: string;
  description?: string | null;
  obligation_type?: string | null;
  due_date?: string | null;
  status?: string | null;
  priority?: string | null;
}

export interface ObligationUpdate {
  assigned_to?: string | null;
  title?: string | null;
  description?: string | null;
  obligation_type?: string | null;
  due_date?: string | null;
  priority?: string | null;
}

export interface ObligationStatusUpdate {
  status: string;
}

@Injectable({
  providedIn: 'root'
})
export class ObligationService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    'http://127.0.0.1:8000/obligations';

  /**
   * Get all obligations visible to the logged-in user.
   */
  getObligations(): Observable<Obligation[]> {
    return this.http.get<Obligation[]>(this.apiUrl);
  }

  /**
   * Get a single obligation by ID.
   */
  getObligation(id: string): Observable<Obligation> {
    return this.http.get<Obligation>(
      `${this.apiUrl}/${id}`
    );
  }

  /**
   * Create a new obligation.
   */
  createObligation(
    obligation: ObligationCreate
  ): Observable<Obligation> {
    return this.http.post<Obligation>(
      this.apiUrl,
      obligation
    );
  }

  /**
   * Update an existing obligation.
   */
  updateObligation(
    id: string,
    obligation: ObligationUpdate
  ): Observable<Obligation> {
    return this.http.put<Obligation>(
      `${this.apiUrl}/${id}`,
      obligation
    );
  }

  /**
   * Update obligation status.
   *
   * Supported workflow includes:
   * Pending → In Progress → Completed
   *
   * The backend also records completed_at when
   * status becomes Completed.
   */
  updateStatus(
    id: string,
    status: string
  ): Observable<Obligation> {
    const data: ObligationStatusUpdate = {
      status
    };

    return this.http.patch<Obligation>(
      `${this.apiUrl}/${id}/status`,
      data
    );
  }

  /**
   * Delete an obligation.
   */
  deleteObligation(id: string): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/${id}`
    );
  }

  /**
   * Get upcoming obligations.
   *
   * @param days Number of days to look ahead.
   */
  getUpcomingObligations(
    days: number = 30
  ): Observable<Obligation[]> {
    return this.http.get<Obligation[]>(
      `${this.apiUrl}/upcoming/list`,
      {
        params: {
          days: days.toString()
        }
      }
    );
  }

  /**
   * Get obligations belonging to a specific contract.
   *
   * The backend contract-specific endpoint is expected
   * at /contracts/{contract_id}/obligations.
   */
  getContractObligations(
    contractId: string
  ): Observable<Obligation[]> {
    return this.http.get<Obligation[]>(
      `http://127.0.0.1:8000/contracts/${contractId}/obligations`
    );
  }
}