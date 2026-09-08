import { Component, OnInit, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import {
  DashboardService,
  DashboardResponse,
  StatusCount
} from '../../services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    DecimalPipe
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {

  private readonly dashboardService = inject(DashboardService);

  totalContracts = 0;
  activeContracts = 0;
  expiredContracts = 0;
  pendingObligations = 0;
  overdueObligations = 0;
  upcomingRenewals = 0;

  compliantCount = 0;
  atRiskCount = 0;
  nonCompliantCount = 0;

  contractStatusDistribution: StatusCount[] = [];
  obligationStatusDistribution: StatusCount[] = [];

  loading = true;
  error = '';
  hasData = false;

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    this.error = '';

    this.dashboardService.getDashboard().subscribe({
      next: (data: DashboardResponse) => {
        this.totalContracts =
          data.contracts.total_contracts;

        this.activeContracts =
          data.contracts.active_contracts;

        this.expiredContracts =
          data.contracts.expired_contracts;

        this.pendingObligations =
          data.obligations.pending_obligations;

        this.overdueObligations =
          data.obligations.overdue_obligations;

        this.upcomingRenewals =
          data.renewals.upcoming_renewals.length;

        this.compliantCount =
          data.compliance.compliant_contracts;

        this.atRiskCount =
          data.compliance.high_risk_contracts;

        this.nonCompliantCount =
          data.compliance.non_compliant_contracts;

        this.contractStatusDistribution =
          data.contract_status_distribution ?? [];

        this.obligationStatusDistribution =
          data.obligation_status_distribution ?? [];

        this.hasData = this.checkHasData(data);

        this.loading = false;
      },

      error: (err) => {
        console.error('Dashboard API error:', err);

        this.error =
          'Unable to load dashboard data. Please check the backend and login status.';

        this.loading = false;
        this.hasData = false;
      }
    });
  }

  private checkHasData(
    data: DashboardResponse
  ): boolean {

    const contractData =
      data.contracts.total_contracts > 0;

    const obligationData =
      data.obligations.total_obligations > 0;

    const renewalData =
      data.renewals.upcoming_renewals.length > 0;

    const complianceData =
      data.compliance.total_contracts > 0;

    const contractStatuses =
      data.contract_status_distribution?.length > 0;

    const obligationStatuses =
      data.obligation_status_distribution?.length > 0;

    return (
      contractData ||
      obligationData ||
      renewalData ||
      complianceData ||
      contractStatuses ||
      obligationStatuses
    );
  }

  getStatusPercentage(
    item: StatusCount,
    distribution: StatusCount[]
  ): number {

    const total = distribution.reduce(
      (sum, status) => sum + status.count,
      0
    );

    if (total === 0) {
      return 0;
    }

    return (item.count / total) * 100;
  }
}