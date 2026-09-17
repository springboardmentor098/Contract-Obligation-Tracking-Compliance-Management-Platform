import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Activity {
  id: number;
  user_id: number;
  contract_id: number;
  activity_type: string;
  description: string | null;
  created_at: string;
}

export interface AuditLog {
  id: number;
  user_id: number;
  contract_id: number;
  action: string;
  details: string | null;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuditService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getActivities(): Observable<Activity[]> {
    return this.http.get<Activity[]>(`${this.apiUrl}/audit/activities`);
  }

  getAuditLogs(): Observable<AuditLog[]> {
    return this.http.get<AuditLog[]>(`${this.apiUrl}/audit/logs`);
  }
}
