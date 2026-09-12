import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Contract {
  id: number;
  contract_number: string;
  title: string;
  category: string;
  description: string;
  party_name: string;
  start_date: string;
  end_date: string;
  status: string;
  owner_id: number;
  assigned_to: number | null;
  reviewed_at: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateContract {
  contract_number: string;
  title: string;
  category: string;
  description: string;
  party_name: string;
  start_date: string;
  end_date: string;
}

export interface UpdateContract {
  title: string;
  category: string;
  description: string;
  party_name: string;
  start_date: string;
  end_date: string;
}

@Injectable({
  providedIn: 'root'
})
export class ContractService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(
    private http: HttpClient
  ) {}

  // =====================================================
  // GET ALL CONTRACTS
  // =====================================================

  getContracts(): Observable<Contract[]> {
    return this.http.get<Contract[]>(
      `${this.apiUrl}/contracts`
    );
  }

  // =====================================================
  // GET SINGLE CONTRACT
  // =====================================================

  getContract(id: number): Observable<Contract> {
    return this.http.get<Contract>(
      `${this.apiUrl}/contracts/${id}`
    );
  }

  // =====================================================
  // CREATE CONTRACT
  // =====================================================

  createContract(
    contract: CreateContract
  ): Observable<Contract> {

    return this.http.post<Contract>(
      `${this.apiUrl}/contracts`,
      contract
    );
  }

  // =====================================================
  // UPDATE CONTRACT
  // =====================================================

  updateContract(
    id: number,
    contract: UpdateContract
  ): Observable<Contract> {

    return this.http.put<Contract>(
      `${this.apiUrl}/contracts/${id}`,
      contract
    );
  }

}