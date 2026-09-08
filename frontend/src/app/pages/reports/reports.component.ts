import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
  ComplianceSummary,
  ObligationSummary,
  RenewalReportItem,
  RenewalSummary,
  ReportService,
  StatusCount
} from '../../services/report.service';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTableModule,
    MatTooltipModule
  ],
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.scss'
})
export class ReportsComponent implements OnInit {
  private readonly reportService = inject(ReportService);

  loading = true;
  error = '';

  contractSummary = {
    total_contracts: 0,
    active_contracts: 0,
    expired_contracts: 0,
    pending_approval: 0
  };

  contractStatusDistribution: StatusCount[] = [];

  obligationSummary: ObligationSummary = {
    total_obligations: 0,
    pending_obligations: 0,
    completed_obligations: 0,
    overdue_obligations: 0
  };

  obligationStatusDistribution: StatusCount[] = [];

  complianceSummary: ComplianceSummary = {
    total_contracts: 0,
    compliant_contracts: 0,
    non_compliant_contracts: 0,
    high_risk_contracts: 0,
    high_risk_obligations: 0,
    average_compliance_score: 0
  };

  renewalSummary: RenewalSummary | null = null;

  upcomingRenewals: RenewalReportItem[] = [];
  expiredRenewals: RenewalReportItem[] = [];
  attentionRenewals: RenewalReportItem[] = [];

  contractDisplayedColumns: string[] = [
    'status',
    'count'
  ];

  obligationDisplayedColumns: string[] = [
    'status',
    'count'
  ];

  renewalDisplayedColumns: string[] = [
    'contract_id',
    'renewal_date',
    'previous_expiry_date',
    'new_expiry_date',
    'status'
  ];

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports(): void {
    this.loading = true;
    this.error = '';

    this.reportService.getDashboard().subscribe({
      next: (dashboard) => {
        this.contractSummary = dashboard.contracts;

        this.contractStatusDistribution =
          dashboard.contract_status_distribution;

        this.obligationSummary = dashboard.obligations;

        this.obligationStatusDistribution =
          dashboard.obligation_status_distribution;

        this.renewalSummary = dashboard.renewals;

        this.upcomingRenewals =
          dashboard.renewals.upcoming_renewals;

        this.complianceSummary = dashboard.compliance;

        this.loading = false;

        this.loadAdditionalRenewalReports();
      },
      error: (error: any) => {
        console.error('Reports dashboard API error:', error);

        this.loading = false;

        this.error = this.getErrorMessage(
          error,
          'Unable to load reports and analytics.'
        );
      }
    });
  }

  loadAdditionalRenewalReports(): void {
    this.reportService.getExpiredRenewals().subscribe({
      next: (renewals: RenewalReportItem[]) => {
        this.expiredRenewals = renewals;
      },
      error: (error: any) => {
        console.error('Expired renewals API error:', error);
      }
    });

    this.reportService.getRenewalsRequiringAttention(30).subscribe({
      next: (renewals: RenewalReportItem[]) => {
        this.attentionRenewals = renewals;
      },
      error: (error: any) => {
        console.error('Renewals requiring attention API error:', error);
      }
    });
  }

  refresh(): void {
    this.loadReports();
  }

  retry(): void {
    this.loadReports();
  }

  getStatusClass(status: string | null | undefined): string {
    if (!status) {
      return 'unknown';
    }

    return status
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  getRenewalStatusClass(
    status: string | null | undefined
  ): string {
    if (!status) {
      return 'unknown';
    }

    return status
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  getComplianceClass(): string {
    if (this.complianceSummary.non_compliant_contracts > 0) {
      return 'non-compliant';
    }

    if (this.complianceSummary.high_risk_contracts > 0) {
      return 'high-risk';
    }

    if (
      this.complianceSummary.compliant_contracts ===
      this.complianceSummary.total_contracts
    ) {
      return 'compliant';
    }

    return 'unknown';
  }

  formatScore(score: number | null | undefined): string {
    if (score === null || score === undefined) {
      return '—';
    }

    return `${score}%`;
  }

  formatDate(date: string | null | undefined): string {
    if (!date) {
      return '—';
    }

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return date;
    }

    return parsedDate.toLocaleDateString();
  }

  private getErrorMessage(
    error: any,
    fallback: string
  ): string {
    if (error?.status === 401) {
      return 'Your session has expired. Please log in again.';
    }

    if (error?.status === 403) {
      return 'You do not have permission to view reports.';
    }

    if (error?.status === 404) {
      return 'Reports endpoint was not found on the backend.';
    }

    if (error?.status === 0) {
      return 'Unable to connect to the backend. Please make sure FastAPI is running.';
    }

    return error?.error?.detail || fallback;
  }
}