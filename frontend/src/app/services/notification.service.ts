import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Notification {
  id: string;
  user_id: string;
  contract_id: string | null;
  obligation_id: string | null;

  notification_type: string;
  title: string;
  message: string;

  scheduled_at: string | null;
  sent_at: string | null;
  read_at: string | null;
  status: string | null;

  created_at: string;
}

export interface NotificationCreate {
  user_id: string;
  contract_id?: string | null;
  obligation_id?: string | null;

  notification_type: string;
  title: string;
  message: string;

  scheduled_at?: string | null;
  status?: string | null;
}

export interface MarkAllReadResponse {
  message: string;
  updated_count: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    'http://127.0.0.1:8000/notifications';

  getNotifications(): Observable<Notification[]> {
    return this.http.get<Notification[]>(
      this.apiUrl
    );
  }

  getUnreadNotifications(): Observable<Notification[]> {
    return this.http.get<Notification[]>(
      `${this.apiUrl}/unread`
    );
  }

  getNotification(
    id: string
  ): Observable<Notification> {
    return this.http.get<Notification>(
      `${this.apiUrl}/${id}`
    );
  }

  markAsRead(
    id: string
  ): Observable<Notification> {
    return this.http.patch<Notification>(
      `${this.apiUrl}/${id}/read`,
      {}
    );
  }

  markAsUnread(
    id: string
  ): Observable<Notification> {
    return this.http.patch<Notification>(
      `${this.apiUrl}/${id}/unread`,
      {}
    );
  }

  markAllAsRead(): Observable<MarkAllReadResponse> {
    return this.http.patch<MarkAllReadResponse>(
      `${this.apiUrl}/read-all`,
      {}
    );
  }

  deleteNotification(
    id: string
  ): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(
      `${this.apiUrl}/${id}`
    );
  }

  createNotification(
    notification: NotificationCreate
  ): Observable<Notification> {
    return this.http.post<Notification>(
      this.apiUrl,
      notification
    );
  }
}