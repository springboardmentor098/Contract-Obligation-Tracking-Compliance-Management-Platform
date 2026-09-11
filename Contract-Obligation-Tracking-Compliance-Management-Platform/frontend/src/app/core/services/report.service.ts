import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class ReportService {
  private readonly api = inject(ApiService);
  summary<T = unknown>(): Observable<T> { return this.api.get<T>('/reports/summary'); }
  dashboard<T = unknown>(): Observable<T> { return this.api.get<T>('/reports/dashboard'); }
}
