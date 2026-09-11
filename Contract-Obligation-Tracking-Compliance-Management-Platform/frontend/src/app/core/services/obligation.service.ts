import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Obligation } from '../models/models';

@Injectable({ providedIn: 'root' })
export class ObligationService {
  private readonly api = inject(ApiService);
  list(): Observable<Obligation[]> { return this.api.get<Obligation[]>('/obligations'); }
  byContract(contractId: number | string): Observable<Obligation[]> {
    return this.api.get<Obligation[]>(`/obligations/contract/${contractId}`);
  }
  create(contractId: number | string, data: Partial<Obligation>): Observable<Obligation> {
    return this.api.post<Obligation>(`/contracts/${contractId}/obligations`, data);
  }
  update(id: number | string, data: Partial<Obligation>): Observable<Obligation> {
    return this.api.put<Obligation>(`/obligations/${id}`, data);
  }
  status(id: number | string, status: string): Observable<Obligation> {
    return this.api.patch<Obligation>(`/obligations/${id}/status`, { status });
  }
}
