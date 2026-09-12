import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


// ===============================
// Obligation Interface
// ===============================

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


// ===============================
// Create Obligation
// ===============================

export interface ObligationCreate {
  contract_id: number;
  title: string;
  description?: string | null;
  obligation_type: string;
  due_date: string;
  assigned_to: number;
}


// ===============================
// Update Obligation
// ===============================

export interface ObligationUpdate {
  title?: string;
  description?: string | null;
  obligation_type?: string;
  due_date?: string;
  assigned_to?: number;
}


// ===============================
// Status Update
// ===============================

export interface ObligationStatusUpdate {
  status: string;
}


// ===============================
// Service
// ===============================

@Injectable({
  providedIn: 'root'
})
export class ObligationService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(
    private http: HttpClient
  ) {}


  // ===============================
  // GET ALL OBLIGATIONS
  // ===============================

  getObligations(): Observable<Obligation[]> {

    return this.http.get<Obligation[]>(
      `${this.apiUrl}/obligations`
    );
  }


  // ===============================
  // GET OBLIGATION BY ID
  // ===============================

  getObligation(
    obligationId: number
  ): Observable<Obligation> {

    return this.http.get<Obligation>(
      `${this.apiUrl}/obligations/${obligationId}`
    );
  }


  // ===============================
  // GET CONTRACT OBLIGATIONS
  // ===============================

  getContractObligations(
    contractId: number
  ): Observable<Obligation[]> {

    return this.http.get<Obligation[]>(
      `${this.apiUrl}/contracts/${contractId}/obligations`
    );
  }


  // ===============================
  // CREATE OBLIGATION
  // ===============================

  createObligation(
    data: ObligationCreate
  ): Observable<Obligation> {

    return this.http.post<Obligation>(
      `${this.apiUrl}/obligations`,
      data
    );
  }


  // ===============================
  // UPDATE OBLIGATION
  // ===============================

  updateObligation(
    obligationId: number,
    data: ObligationUpdate
  ): Observable<Obligation> {

    return this.http.put<Obligation>(
      `${this.apiUrl}/obligations/${obligationId}`,
      data
    );
  }


  // ===============================
  // UPDATE STATUS
  // ===============================

  updateObligationStatus(
    obligationId: number,
    status: string
  ): Observable<Obligation> {

    const data: ObligationStatusUpdate = {
      status
    };

    return this.http.patch<Obligation>(
      `${this.apiUrl}/obligations/${obligationId}/status`,
      data
    );
  }


  // ===============================
  // COMPLETE OBLIGATION
  // ===============================

  completeObligation(
    obligationId: number
  ): Observable<Obligation> {

    return this.http.post<Obligation>(
      `${this.apiUrl}/obligations/${obligationId}/complete`,
      {}
    );
  }

}