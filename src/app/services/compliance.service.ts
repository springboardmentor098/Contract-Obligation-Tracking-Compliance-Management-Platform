import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  ComplianceEvaluation,
  ComplianceRecord
} from '../models/compliance.model';

@Injectable({
  providedIn: 'root'
})
export class ComplianceService {

  private readonly apiUrl = 'http://127.0.0.1:8000/compliance';

  constructor(private readonly http: HttpClient) {}

  // Get current compliance evaluation for all contracts
  getAllCompliance(): Observable<ComplianceEvaluation[]> {
    return this.http.get<ComplianceEvaluation[]>(
      `${this.apiUrl}/`
    );
  }

  // Get current compliance for one contract
  getContractCompliance(
    contractId: number
  ): Observable<ComplianceEvaluation> {
    return this.http.get<ComplianceEvaluation>(
      `${this.apiUrl}/contract/${contractId}`
    );
  }

  // Create and save a compliance evaluation
  createEvaluation(
    contractId: number,
    notes: string
  ): Observable<ComplianceRecord> {

    const requestBody = {
      contract_id: contractId,
      notes: notes
    };

    return this.http.post<ComplianceRecord>(
      `${this.apiUrl}/evaluate/${contractId}`,
      requestBody
    );
  }

  // Get saved compliance records
  getSavedRecords(): Observable<ComplianceRecord[]> {
    return this.http.get<ComplianceRecord[]>(
      `${this.apiUrl}/records`
    );
  }

  // Get one saved compliance record
  getRecord(
    recordId: number
  ): Observable<ComplianceRecord> {
    return this.http.get<ComplianceRecord>(
      `${this.apiUrl}/records/${recordId}`
    );
  }

  // Get compliance history for one contract
  getContractHistory(
    contractId: number
  ): Observable<ComplianceRecord[]> {
    return this.http.get<ComplianceRecord[]>(
      `${this.apiUrl}/contract/${contractId}/history`
    );
  }
}