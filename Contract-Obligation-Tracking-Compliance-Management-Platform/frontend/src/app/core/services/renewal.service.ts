import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Renewal } from '../models/models';

@Injectable({ providedIn: 'root' })
export class RenewalService {
  private readonly api = inject(ApiService);
  list(): Observable<Renewal[]> { return this.api.get<Renewal[]>('/renewals'); }
  get(id: number | string): Observable<Renewal> { return this.api.get<Renewal>(`/renewals/${id}`); }
  create(data: Partial<Renewal>): Observable<Renewal> { return this.api.post<Renewal>('/renewals', data); }
  update(id: number | string, data: Partial<Renewal>): Observable<Renewal> {
    return this.api.put<Renewal>(`/renewals/${id}`, data);
  }
  status(id: number | string, status: string): Observable<Renewal> {
    return this.api.patch<Renewal>(`/renewals/${id}/status`, { status });
  }
}
