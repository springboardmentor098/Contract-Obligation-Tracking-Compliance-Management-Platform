import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  Contract,
  CreateContractRequest,
  UpdateContractRequest,
  UpdateContractStatusRequest
} from '../models/contract.model';

@Injectable({
  providedIn: 'root'
})
export class ContractService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://127.0.0.1:8000/contracts';

  getContracts(): Observable<Contract[]> {
    return this.http.get<Contract[]>(this.apiUrl);
  }

  getContract(id: number): Observable<Contract> {
    return this.http.get<Contract>(`${this.apiUrl}/${id}`);
  }

  createContract(
    contract: CreateContractRequest
  ): Observable<Contract> {
    return this.http.post<Contract>(
      this.apiUrl,
      contract
    );
  }

  updateContract(
    id: number,
    contract: UpdateContractRequest
  ): Observable<Contract> {
    return this.http.put<Contract>(
      `${this.apiUrl}/${id}`,
      contract
    );
  }

  deleteContract(id: number): Observable<string> {
    return this.http.delete(
      `${this.apiUrl}/${id}`,
      {
        responseType: 'text'
      }
    );
  }

  updateStatus(
    id: number,
    status: string
  ): Observable<Contract> {

    const body: UpdateContractStatusRequest = {
      status
    };

    return this.http.patch<Contract>(
      `${this.apiUrl}/${id}/status`,
      body
    );
  }

  submitForReview(id: number): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/${id}/submit-review`,
      {}
    );
  }

  approve(id: number): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/${id}/approve`,
      {}
    );
  }

  activate(id: number): Observable<Contract> {
    return this.http.post<Contract>(
      `${this.apiUrl}/${id}/activate`,
      {}
    );
  }
}