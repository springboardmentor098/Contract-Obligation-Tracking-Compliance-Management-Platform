import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Contract {
  id: number;
  contract_number: string;
  title: string;
  category: string;
  description: string | null;
  counterparty_name: string;
  start_date: string;
  end_date: string | null;
  created_by: number;
  assigned_to: number | null;
  status: string;
  reviewed_at: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContractCreate {
  contract_number: string;
  title: string;
  category: string;
  description?: string | null;
  counterparty_name: string;
  start_date: string;
  end_date?: string | null;
  assigned_to?: number | null;
}

@Injectable({
  providedIn: 'root'
})
export class ContractService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  getContracts(): Observable<Contract[]> {
    return this.http.get<Contract[]>(
      `${this.apiUrl}/contracts`
    );
  }

  getContract(id: number): Observable<Contract> {
    return this.http.get<Contract>(
      `${this.apiUrl}/contracts/${id}`
    );
  }

  createContract(data: ContractCreate): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/contracts`,
      data
    );
  }

  updateContract(
    id: number,
    data: Partial<ContractCreate>
  ): Observable<Contract> {
    return this.http.put<Contract>(
      `${this.apiUrl}/contracts/${id}`,
      data
    );
  }

  deleteContract(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/contracts/${id}`
    );
  }

  updateStatus(
    id: number,
    newStatus: string
  ): Observable<Contract> {
    return this.http.patch<Contract>(
      `${this.apiUrl}/contracts/${id}/status`,
      null,
      {
        params: {
          new_status: newStatus
        }
      }
    );
  }
}
