import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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
}

@Injectable({
  providedIn: 'root'
})
export class Notifications {

  private readonly baseUrl = 'http://127.0.0.1:8000/notifications';

  constructor(private http: HttpClient) {}

  getNotifications(): Observable<Notification[]> {
    return this.http.get<Notification[]>(this.baseUrl);
  }
}