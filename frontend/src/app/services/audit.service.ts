import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface AuditLog {
  id: string;
  user_id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  old_values: Record<string, unknown> | null;
  new_values: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface AuditLogResponse {
  data: AuditLog[];
  total: number;
}

export interface AuditLogFilters {
  entity_type?: string;
  action?: string;
  user_id?: string;
  date_from?: string;
  date_to?: string;
  skip?: number;
  limit?: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuditService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://127.0.0.1:8000/audit-logs';

  getAuditLogs(filters: AuditLogFilters = {}): Observable<AuditLogResponse> {
    let params = new HttpParams();

    if (filters.entity_type) {
      params = params.set('entity_type', filters.entity_type);
    }

    if (filters.action) {
      params = params.set('action', filters.action);
    }

    if (filters.user_id) {
      params = params.set('user_id', filters.user_id);
    }

    if (filters.date_from) {
      params = params.set('date_from', filters.date_from);
    }

    if (filters.date_to) {
      params = params.set('date_to', filters.date_to);
    }

    params = params.set('skip', (filters.skip ?? 0).toString());
    params = params.set('limit', (filters.limit ?? 100).toString());

    return this.http.get<AuditLogResponse>(this.apiUrl, { params });
  }

  getAuditLog(id: string): Observable<AuditLog> {
    return this.http.get<AuditLog>(`${this.apiUrl}/${id}`);
  }
}