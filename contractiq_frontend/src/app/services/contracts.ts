import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Contract {
  id: number;
  title: string;
  contract_number: string;
  category: string;
  description: string | null;
  start_date: string;
  end_date: string;
  status: string;
  created_by: number;
  assigned_to: number | null;
  reviewed_at: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContractCreate {
  title: string;
  contract_number: string;
  category: string;
  description?: string;
  start_date: string;
  end_date: string;
}

export interface ContractUpdate {
  title?: string;
  category?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ContractsService {

  private apiUrl = 'http://127.0.0.1:8000/contracts';

  constructor(private http: HttpClient) {}

  getContracts(): Observable<Contract[]> {
    return this.http.get<Contract[]>(this.apiUrl);
  }

  getContract(id: number): Observable<Contract> {
    return this.http.get<Contract>(`${this.apiUrl}/${id}`);
  }

  createContract(contract: ContractCreate): Observable<Contract> {
    return this.http.post<Contract>(this.apiUrl, contract);
  }

  updateContract(
    id: number,
    contract: ContractUpdate
  ): Observable<Contract> {
    return this.http.put<Contract>(
      `${this.apiUrl}/${id}`,
      contract
    );
  }

  getContractObligations(id: number): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.apiUrl}/${id}/obligations`
    );
  }

  getContractCompliance(id: number): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/${id}/compliance`
    );
  }

  assignContract(
    id: number,
    assignedTo: number
  ): Observable<Contract> {
    return this.http.patch<Contract>(
      `${this.apiUrl}/${id}/assign`,
      { assigned_to: assignedTo }
    );
  }

  updateStatus(
    id: number,
    status: string
  ): Observable<Contract> {
    return this.http.patch<Contract>(
      `${this.apiUrl}/${id}/status`,
      { status }
    );
  }

  submitForReview(id: number): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/${id}/submit-review`,
      {}
    );
  }

  approveContract(id: number): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/${id}/approve`,
      {}
    );
  }

  activateContract(id: number): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/${id}/activate`,
      {}
    );
  }
}
