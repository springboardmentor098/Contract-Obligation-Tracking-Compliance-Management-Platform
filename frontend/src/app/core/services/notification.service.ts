import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Notification {
  id: number;
  user_id: number;
  contract_id: number | null;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationResponse {
  value: Notification[];
  Count: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  getNotifications(): Observable<NotificationResponse> {
    return this.http.get<NotificationResponse>(
      `${this.apiUrl}/notifications`
    );
  }

  getNotification(id: number): Observable<Notification> {
    return this.http.get<Notification>(
      `${this.apiUrl}/notifications/${id}`
    );
  }
}
