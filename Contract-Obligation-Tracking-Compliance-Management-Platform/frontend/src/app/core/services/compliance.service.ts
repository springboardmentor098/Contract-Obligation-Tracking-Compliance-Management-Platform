import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ComplianceRecord } from '../models/models';

@Injectable({ providedIn: 'root' })
export class ComplianceService {
  private readonly api = inject(ApiService);
  list(): Observable<ComplianceRecord[]> { return this.api.get<ComplianceRecord[]>('/compliance'); }
}
