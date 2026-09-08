import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Contract {
  id: string;
  title: string;
  contract_number: string;
  category: string | null;
  description: string | null;
  counterparty_name: string | null;
  start_date: string | null;
  end_date: string | null;
  contract_value: number | null;
  currency: string | null;
  status: string;
  created_by: string;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContractCreate {
  title: string;
  contract_number: string;
  category: string;
  description?: string | null;
  counterparty_name?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  contract_value?: number | null;
  currency?: string | null;
  assigned_to?: string | null;
}

export interface ContractUpdate {
  title?: string | null;
  category?: string | null;
  description?: string | null;
  counterparty_name?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  contract_value?: number | null;
  currency?: string | null;
  assigned_to?: string | null;
}

export interface ContractStatusUpdate {
  status: string;
}

export interface ContractAssignment {
  assigned_to: string;
}

@Injectable({
  providedIn: 'root'
})
export class ContractService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://127.0.0.1:8000/contracts';

  /**
   * Get all contracts available to the logged-in user.
   */
  getContracts(): Observable<Contract[]> {
    return this.http.get<Contract[]>(this.apiUrl);
  }

  /**
   * Get a single contract by ID.
   */
  getContract(id: string): Observable<Contract> {
    return this.http.get<Contract>(
      `${this.apiUrl}/${id}`
    );
  }

  /**
   * Create a new contract.
   */
  createContract(
    contract: ContractCreate
  ): Observable<Contract> {
    return this.http.post<Contract>(
      this.apiUrl,
      contract
    );
  }

  /**
   * Update an existing contract.
   */
  updateContract(
    id: string,
    contract: ContractUpdate
  ): Observable<Contract> {
    return this.http.put<Contract>(
      `${this.apiUrl}/${id}`,
      contract
    );
  }

  /**
   * Assign a contract to a user.
   */
  assignContract(
    id: string,
    assignment: ContractAssignment
  ): Observable<Contract> {
    return this.http.patch<Contract>(
      `${this.apiUrl}/${id}/assign`,
      assignment
    );
  }

  /**
   * Update contract status.
   */
  updateStatus(
    id: string,
    status: string
  ): Observable<Contract> {
    return this.http.patch<Contract>(
      `${this.apiUrl}/${id}/status`,
      {
        status
      }
    );
  }

  /**
   * Submit a Draft contract for review.
   */
  submitForReview(
    id: string
  ): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/${id}/submit-review`,
      {}
    );
  }

  /**
   * Approve a contract.
   */
  approveContract(
    id: string
  ): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/${id}/approve`,
      {}
    );
  }

  /**
   * Activate an approved contract.
   */
  activateContract(
    id: string
  ): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/${id}/activate`,
      {}
    );
  }

  /**
   * Delete a contract.
   */
  deleteContract(
    id: string
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/${id}`
    );
  }
}