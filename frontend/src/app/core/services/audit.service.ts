import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface AuditLog {
  id: number;
  user_id: number;
  contract_id: number | null;
  entity_type: string | null;
  entity_id: number | null;
  action: string;
  details: string | null;
  created_at: string;
}

export interface AuditResponse {
  value: AuditLog[];
  Count: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuditService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  getAuditLogs(): Observable<AuditResponse> {
    return this.http.get<AuditResponse>(
      `${this.apiUrl}/audit-logs`
    );
  }
}
