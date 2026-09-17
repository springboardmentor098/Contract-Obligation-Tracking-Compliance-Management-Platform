import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Notification } from '../models/notification.model';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {

  private readonly apiUrl =
    'http://127.0.0.1:8000/notifications';

  constructor(
    private readonly http: HttpClient
  ) {}

  getNotifications(): Observable<Notification[]> {
    return this.http.get<Notification[]>(
      this.apiUrl
    );
  }

  getNotification(
    id: number
  ): Observable<Notification> {
    return this.http.get<Notification>(
      `${this.apiUrl}/${id}`
    );
  }

  markAsRead(
    id: number
  ): Observable<{
    id: number;
    status: string;
    read_at: string;
  }> {
    return this.http.patch<{
      id: number;
      status: string;
      read_at: string;
    }>(
      `${this.apiUrl}/${id}/read`,
      {}
    );
  }

  markAllAsRead(): Observable<{
    message: string;
    updated_count: number;
  }> {
    return this.http.patch<{
      message: string;
      updated_count: number;
    }>(
      `${this.apiUrl}/read-all`,
      {}
    );
  }
}