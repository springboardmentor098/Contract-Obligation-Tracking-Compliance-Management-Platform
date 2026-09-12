import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Contract {
  id: number;
  title: string;
  contract_number: string;
  category: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  status: string;
  created_by: number;
  assigned_to: number;
  created_at: string;
  updated_at: string;
  reviewed_at: string | null;
  approved_at: string | null;
}

export interface ContractCreate {
  title: string;
  contract_number: string;
  category: string;
  description?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface ContractUpdate {
  title?: string;
  category?: string;
  description?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface ContractStatusUpdate {
  status: string;
}

export interface ContractAssignment {
  assigned_to: number;
}

@Injectable({
  providedIn: 'root'
})
export class Contracts {

  private readonly baseUrl = 'http://127.0.0.1:8000/contracts';

  constructor(private http: HttpClient) {}

  getContracts(): Observable<Contract[]> {
    return this.http.get<Contract[]>(this.baseUrl);
  }

  getContractById(contractId: number): Observable<Contract> {
    return this.http.get<Contract>(
      `${this.baseUrl}/${contractId}`
    );
  }

  createContract(data: ContractCreate): Observable<Contract> {
    return this.http.post<Contract>(
      this.baseUrl,
      data
    );
  }

  updateContract(
    contractId: number,
    data: ContractUpdate
  ): Observable<Contract> {
    return this.http.put<Contract>(
      `${this.baseUrl}/${contractId}`,
      data
    );
  }

  updateContractStatus(
    contractId: number,
    data: ContractStatusUpdate
  ): Observable<Contract> {
    return this.http.patch<Contract>(
      `${this.baseUrl}/${contractId}/status`,
      data
    );
  }

  submitForReview(contractId: number): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.baseUrl}/${contractId}/submit-review`,
      {}
    );
  }

  approveContract(contractId: number): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.baseUrl}/${contractId}/approve`,
      {}
    );
  }

  activateContract(contractId: number): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.baseUrl}/${contractId}/activate`,
      {}
    );
  }

  assignContract(
    contractId: number,
    data: ContractAssignment
  ): Observable<Contract> {
    return this.http.patch<Contract>(
      `${this.baseUrl}/${contractId}/assignment`,
      data
    );
  }

  getContractObligations(contractId: number): Observable<unknown[]> {
    return this.http.get<unknown[]>(
      `${this.baseUrl}/${contractId}/obligations`
    );
  }

  getContractRenewals(contractId: number): Observable<unknown[]> {
    return this.http.get<unknown[]>(
      `${this.baseUrl}/${contractId}/renewals`
    );
  }
}