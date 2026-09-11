import { Injectable, inject } from '@angular/core';
import { forkJoin, map, Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Contract, Obligation, Renewal, ComplianceRecord, DashboardSummary } from '../models/models';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly api = inject(ApiService);

  getSummary(): Observable<DashboardSummary> {
    return forkJoin({
      contracts: this.api.get<Contract[]>('/contracts'),
      obligations: this.api.get<Obligation[]>('/obligations'),
      renewals: this.api.get<Renewal[]>('/renewals'),
      compliance: this.api.get<ComplianceRecord[]>('/compliance')
    }).pipe(map(({ contracts, obligations, renewals, compliance }) => {
      const today = new Date();
      const active = contracts.filter(c => c.status === 'Active').length;
      const expired = contracts.filter(c => c.status === 'Expired').length;
      const pending = obligations.filter(o => o.status === 'Pending').length;
      const overdue = obligations.filter(o =>
        o.status === 'Overdue' || (!!o.due_date && new Date(o.due_date) < today && o.status !== 'Completed')
      ).length;
      const upcoming = renewals.filter(r => r.status === 'Upcoming').length;
      const contractDist: Record<string, number> = {};
      const obligationDist: Record<string, number> = {};
      const complianceDist: Record<string, number> = {};
      contracts.forEach(c => contractDist[c.status] = (contractDist[c.status] ?? 0) + 1);
      obligations.forEach(o => obligationDist[o.status] = (obligationDist[o.status] ?? 0) + 1);
      compliance.forEach(c => complianceDist[c.status] = (complianceDist[c.status] ?? 0) + 1);
      return {
        total_contracts: contracts.length,
        active_contracts: active,
        expired_contracts: expired,
        pending_obligations: pending,
        overdue_obligations: overdue,
        upcoming_renewals: upcoming,
        compliance_summary: complianceDist,
        contract_status_distribution: contractDist,
        obligation_status_distribution: obligationDist
      };
    }));
  }
}
