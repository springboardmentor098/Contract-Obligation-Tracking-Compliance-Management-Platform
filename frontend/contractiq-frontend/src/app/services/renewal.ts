import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


// ========================================
// RENEWAL MODEL
// ========================================

export interface Renewal {
  id: number;
  contract_id: number;

  renewal_date: string;
  previous_expiry_date: string;
  new_expiry_date: string;

  status: string;

  assigned_to: number;

  notes: string | null;

  created_at: string;
  updated_at: string;
}


// ========================================
// CREATE RENEWAL
// ========================================

export interface RenewalCreate {
  contract_id: number;

  renewal_date: string;
  previous_expiry_date: string;
  new_expiry_date: string;

  assigned_to: number;

  notes?: string | null;
}


// ========================================
// UPDATE RENEWAL
// ========================================

export interface RenewalUpdate {
  renewal_date?: string;
  previous_expiry_date?: string;
  new_expiry_date?: string;

  assigned_to?: number;

  notes?: string | null;
}


// ========================================
// STATUS UPDATE
// ========================================

export interface RenewalStatusUpdate {
  status: string;
}


// ========================================
// SERVICE
// ========================================

@Injectable({
  providedIn: 'root'
})
export class RenewalService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(
    private http: HttpClient
  ) {}


  // ========================================
  // GET ALL RENEWALS
  // ========================================

  getRenewals(): Observable<Renewal[]> {

    return this.http.get<Renewal[]>(
      `${this.apiUrl}/renewals`
    );

  }


  // ========================================
  // GET SINGLE RENEWAL
  // ========================================

  getRenewal(
    renewalId: number
  ): Observable<Renewal> {

    return this.http.get<Renewal>(
      `${this.apiUrl}/renewals/${renewalId}`
    );

  }


  // ========================================
  // GET CONTRACT RENEWALS
  // ========================================

  getContractRenewals(
    contractId: number
  ): Observable<Renewal[]> {

    return this.http.get<Renewal[]>(
      `${this.apiUrl}/contracts/${contractId}/renewals`
    );

  }


  // ========================================
  // CREATE RENEWAL
  // ========================================

  createRenewal(
    data: RenewalCreate
  ): Observable<Renewal> {

    return this.http.post<Renewal>(
      `${this.apiUrl}/renewals`,
      data
    );

  }


  // ========================================
  // UPDATE RENEWAL
  // ========================================

  updateRenewal(
    renewalId: number,
    data: RenewalUpdate
  ): Observable<Renewal> {

    return this.http.put<Renewal>(
      `${this.apiUrl}/renewals/${renewalId}`,
      data
    );

  }


  // ========================================
  // UPDATE STATUS
  // ========================================

  updateRenewalStatus(
    renewalId: number,
    status: string
  ): Observable<Renewal> {

    const data: RenewalStatusUpdate = {
      status
    };

    return this.http.patch<Renewal>(
      `${this.apiUrl}/renewals/${renewalId}/status`,
      data
    );

  }


  // ========================================
  // RENEW CONTRACT
  // ========================================

  renewContract(
    renewalId: number
  ): Observable<Renewal> {

    return this.http.post<Renewal>(
      `${this.apiUrl}/renewals/${renewalId}/renew`,
      {}
    );

  }

}