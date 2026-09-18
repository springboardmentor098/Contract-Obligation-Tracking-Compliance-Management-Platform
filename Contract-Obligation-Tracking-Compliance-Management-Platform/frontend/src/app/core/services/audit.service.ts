import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Activity } from '../models/models';

@Injectable({ providedIn: 'root' })
export class AuditService {
  private readonly api = inject(ApiService);
  list(): Observable<Activity[]> { return this.api.get<Activity[]>('/audit'); }
}
