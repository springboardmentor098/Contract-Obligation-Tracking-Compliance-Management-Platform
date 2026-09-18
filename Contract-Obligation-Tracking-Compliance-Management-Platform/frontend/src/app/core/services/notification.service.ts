import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Notification } from '../models/models';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly api = inject(ApiService);
  list(): Observable<Notification[]> { return this.api.get<Notification[]>('/notifications'); }
  get(id: number | string): Observable<Notification> { return this.api.get<Notification>(`/notifications/${id}`); }
  read(id: number | string): Observable<Notification> { return this.api.patch<Notification>(`/notifications/${id}/read`); }
  unread(id: number | string): Observable<Notification> { return this.api.patch<Notification>(`/notifications/${id}/unread`); }
}
