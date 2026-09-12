import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface AuditLog {
  id: number;

  user_id: number | null;

  action: string;

  entity_type: string;

  entity_id: number | null;

  old_values: Record<string, any> | null;

  new_values: Record<string, any> | null;

  ip_address: string | null;

  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuditService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(
    private http: HttpClient
  ) {}

  getAuditLogs(): Observable<AuditLog[]> {
    return this.http.get<AuditLog[]>(
      `${this.apiUrl}/audit/logs`
    );
  }
}