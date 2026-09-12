import { Injectable } from '@angular/core';
import {
  HttpClient
} from '@angular/common/http';

import {
  Observable
} from 'rxjs';


// =========================
// NOTIFICATION INTERFACE
// =========================

export interface Notification {

  id: number;

  user_id: number;

  contract_id: number | null;

  obligation_id: number | null;

  notification_type: string;

  title: string;

  message: string;

  status: string;

  scheduled_at: string | null;

  sent_at: string | null;

  read_at: string | null;

  created_at: string;

  updated_at: string;

}


// =========================
// MARK ALL RESPONSE
// =========================

export interface MarkAllReadResponse {

  message: string;

  count: number;

}


// =========================
// SERVICE
// =========================

@Injectable({
  providedIn: 'root'
})


export class NotificationService {

  private apiUrl =
    'http://127.0.0.1:8000';


  constructor(
    private http: HttpClient
  ) {}


  // =========================
  // GET ALL
  // =========================

  getNotifications():
    Observable<Notification[]> {

    return this.http.get<Notification[]>(
      `${this.apiUrl}/notifications`
    );

  }


  // =========================
  // GET SINGLE
  // =========================

  getNotification(
    notificationId: number
  ): Observable<Notification> {

    return this.http.get<Notification>(
      `${this.apiUrl}/notifications/${notificationId}`
    );

  }


  // =========================
  // MARK ONE AS READ
  // =========================

  markAsRead(
    notificationId: number
  ): Observable<Notification> {

    return this.http.patch<Notification>(
      `${this.apiUrl}/notifications/${notificationId}/read`,
      {}
    );

  }


  // =========================
  // MARK ALL AS READ
  // =========================

  markAllAsRead():
    Observable<MarkAllReadResponse> {

    return this.http.patch<MarkAllReadResponse>(
      `${this.apiUrl}/notifications/read-all`,
      {}
    );

  }

}