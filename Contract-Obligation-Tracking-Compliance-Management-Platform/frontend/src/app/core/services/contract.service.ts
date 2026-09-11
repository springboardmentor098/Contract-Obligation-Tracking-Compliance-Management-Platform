import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Contract } from '../models/models';

@Injectable({ providedIn: 'root' })
export class ContractService {
  private readonly api = inject(ApiService);
  list(): Observable<Contract[]> { return this.api.get<Contract[]>('/contracts'); }
  get(id: number | string): Observable<Contract> { return this.api.get<Contract>(`/contracts/${id}`); }
  create(data: Partial<Contract>): Observable<Contract> { return this.api.post<Contract>('/contracts', data); }
  update(id: number | string, data: Partial<Contract>): Observable<Contract> { return this.api.put<Contract>(`/contracts/${id}`, data); }
  remove(id: number | string): Observable<void> { return this.api.delete<void>(`/contracts/${id}`); }
  updateStatus(id: number | string, status: string): Observable<Contract> {
    return this.api.patch<Contract>(`/contracts/${id}/status`, { status });
  }
  submitReview(id: number | string): Observable<Contract> { return this.api.post<Contract>(`/contracts/${id}/submit-review`, {}); }
  approve(id: number | string): Observable<Contract> { return this.api.post<Contract>(`/contracts/${id}/approve`, {}); }
}
