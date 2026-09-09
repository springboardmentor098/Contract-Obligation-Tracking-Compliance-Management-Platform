import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DashboardSummary } from '../models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class DashboardService { constructor(private http: HttpClient) {} getSummary(): Observable<DashboardSummary> { return this.http.get<DashboardSummary>(`${environment.apiBaseUrl}/dashboard/summary`); } }