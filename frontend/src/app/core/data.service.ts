import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE } from './api-base';
import {
  Contract, ContractListItem, Obligation, ObligationListItem, Renewal,
  ComplianceListItem, ComplianceSummary, ContractCompliance, HighRiskContract,
  NonCompliantContract, AppNotification, DashboardSummary, User
} from './models';

@Injectable({ providedIn: 'root' })
export class ContractsService {
  private http = inject(HttpClient);
  list(): Observable<ContractListItem[]> { return this.http.get<ContractListItem[]>(`${API_BASE}/contracts`); }
  get(id: number): Observable<Contract> { return this.http.get<Contract>(`${API_BASE}/contracts/${id}`); }
  create(payload: any): Observable<Contract> { return this.http.post<Contract>(`${API_BASE}/contracts`, payload); }
  update(id: number, payload: any): Observable<Contract> { return this.http.put<Contract>(`${API_BASE}/contracts/${id}`, payload); }
  setStatus(id: number, status: string): Observable<Contract> { return this.http.patch<Contract>(`${API_BASE}/contracts/${id}/status`, { status }); }
  submitReview(id: number): Observable<Contract> { return this.http.post<Contract>(`${API_BASE}/contracts/${id}/submit-review`, {}); }
  approve(id: number): Observable<Contract> { return this.http.post<Contract>(`${API_BASE}/contracts/${id}/approve`, {}); }
  activate(id: number): Observable<Contract> { return this.http.post<Contract>(`${API_BASE}/contracts/${id}/activate`, {}); }
  assign(id: number, assigned_to: number): Observable<Contract> { return this.http.patch<Contract>(`${API_BASE}/contracts/${id}/assign`, { assigned_to }); }
  compliance(id: number): Observable<ContractCompliance> { return this.http.get<ContractCompliance>(`${API_BASE}/contracts/${id}/compliance`); }
}

@Injectable({ providedIn: 'root' })
export class ObligationsService {
  private http = inject(HttpClient);
  list(): Observable<ObligationListItem[]> { return this.http.get<ObligationListItem[]>(`${API_BASE}/obligations`); }
  get(id: number): Observable<Obligation> { return this.http.get<Obligation>(`${API_BASE}/obligations/${id}`); }
  forContract(contractId: number): Observable<ObligationListItem[]> { return this.http.get<ObligationListItem[]>(`${API_BASE}/contracts/${contractId}/obligations`); }
  create(payload: any): Observable<Obligation> { return this.http.post<Obligation>(`${API_BASE}/obligations`, payload); }
  update(id: number, payload: any): Observable<Obligation> { return this.http.put<Obligation>(`${API_BASE}/obligations/${id}`, payload); }
  setStatus(id: number, status: string): Observable<Obligation> { return this.http.patch<Obligation>(`${API_BASE}/obligations/${id}/status`, { status }); }
  complete(id: number): Observable<Obligation> { return this.http.post<Obligation>(`${API_BASE}/obligations/${id}/complete`, {}); }
}

@Injectable({ providedIn: 'root' })
export class RenewalsService {
  private http = inject(HttpClient);
  list(): Observable<Renewal[]> { return this.http.get<Renewal[]>(`${API_BASE}/renewals`); }
  get(id: number): Observable<Renewal> { return this.http.get<Renewal>(`${API_BASE}/renewals/${id}`); }
  forContract(contractId: number): Observable<Renewal[]> { return this.http.get<Renewal[]>(`${API_BASE}/contracts/${contractId}/renewals`); }
  create(payload: any): Observable<Renewal> { return this.http.post<Renewal>(`${API_BASE}/renewals`, payload); }
  update(id: number, payload: any): Observable<Renewal> { return this.http.put<Renewal>(`${API_BASE}/renewals/${id}`, payload); }
  setStatus(id: number, status: string): Observable<Renewal> { return this.http.patch<Renewal>(`${API_BASE}/renewals/${id}/status`, { status }); }
  renew(id: number): Observable<Renewal> { return this.http.post<Renewal>(`${API_BASE}/renewals/${id}/renew`, {}); }
}

@Injectable({ providedIn: 'root' })
export class ComplianceService {
  private http = inject(HttpClient);
  summary(): Observable<ComplianceSummary> { return this.http.get<ComplianceSummary>(`${API_BASE}/compliance/summary`); }
  list(): Observable<ComplianceListItem[]> { return this.http.get<ComplianceListItem[]>(`${API_BASE}/compliance`); }
  nonCompliant(): Observable<NonCompliantContract[]> { return this.http.get<NonCompliantContract[]>(`${API_BASE}/compliance/non-compliant`); }
  highRisk(): Observable<HighRiskContract[]> { return this.http.get<HighRiskContract[]>(`${API_BASE}/compliance/high-risk`); }
}

@Injectable({ providedIn: 'root' })
export class NotificationsService {
  private http = inject(HttpClient);
  list(): Observable<AppNotification[]> { return this.http.get<AppNotification[]>(`${API_BASE}/notifications`); }
  markRead(id: number): Observable<AppNotification> { return this.http.patch<AppNotification>(`${API_BASE}/notifications/${id}/read`, {}); }
  markAllRead(): Observable<any> { return this.http.patch(`${API_BASE}/notifications/read-all`, {}); }
}

@Injectable({ providedIn: 'root' })
export class ReportsService {
  private http = inject(HttpClient);
  dashboard(): Observable<DashboardSummary> { return this.http.get<DashboardSummary>(`${API_BASE}/dashboard/summary`); }
  overdueObligations(): Observable<any> { return this.http.get(`${API_BASE}/dashboard/overdue-obligations`); }
  contractsSummary(): Observable<any> { return this.http.get(`${API_BASE}/reports/contracts/summary`); }
  obligationsSummary(): Observable<any> { return this.http.get(`${API_BASE}/reports/obligations/summary`); }
  renewalsSummary(): Observable<any> { return this.http.get(`${API_BASE}/reports/renewals/summary`); }
  complianceSummary(): Observable<any> { return this.http.get(`${API_BASE}/reports/compliance/summary`); }
  risk(): Observable<any> { return this.http.get(`${API_BASE}/reports/risk`); }
  export(kind: string, fmt: 'excel' | 'pdf'): Observable<Blob> {
    return this.http.get(`${API_BASE}/reports/${kind}/export/${fmt}`, { responseType: 'blob' });
  }
}

@Injectable({ providedIn: 'root' })
export class UsersService {
  private http = inject(HttpClient);
  list(): Observable<User[]> { return this.http.get<User[]>(`${API_BASE}/users`); }
  get(id: number): Observable<User> { return this.http.get<User>(`${API_BASE}/users/${id}`); }
  updateRole(id: number, role: string): Observable<User> { return this.http.patch<User>(`${API_BASE}/users/${id}/role`, { role }); }
  deactivate(id: number): Observable<any> { return this.http.delete(`${API_BASE}/users/${id}`); }
  updateMe(payload: any): Observable<User> { return this.http.put<User>(`${API_BASE}/users/me`, payload); }
}
