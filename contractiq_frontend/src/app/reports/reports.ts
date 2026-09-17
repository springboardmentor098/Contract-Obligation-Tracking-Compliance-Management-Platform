import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import {
  ReportsService,
  ContractStats,
  ObligationStats,
  RenewalStats,
  ComplianceStats,
  RiskSummary
} from '../services/reports';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './reports.html',
  styleUrl: './reports.css'
})
export class Reports implements OnInit {

  contractStats: ContractStats | null = null;
  obligationStats: ObligationStats | null = null;
  renewalStats: RenewalStats | null = null;
  complianceStats: ComplianceStats | null = null;
  riskSummary: RiskSummary | null = null;

  loading = false;
  errorMessage = '';
  successMessage = '';

  selectedReportType = 'all';
  startDate = '';
  endDate = '';

  constructor(
    private reportsService: ReportsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports(): void {
    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.contractStats = null;
    this.obligationStats = null;
    this.renewalStats = null;
    this.complianceStats = null;
    this.riskSummary = null;

    switch (this.selectedReportType) {

      case 'contracts':
        this.loadContracts();
        break;

      case 'obligations':
        this.loadObligations();
        break;

      case 'renewals':
        this.loadRenewals();
        break;

      case 'compliance':
        this.loadCompliance();
        break;

      default:
        this.loadAllReports();
        break;
    }
  }

  private loadContracts(): void {
    this.reportsService.getContractStats(
      this.startDate || undefined,
      this.endDate || undefined
    ).subscribe({
      next: (data) => {
        this.contractStats = data;
        this.finishLoading();
      },
      error: (error) => {
        console.error('Contract report error:', error);
        this.errorMessage = 'Unable to load the contract report.';
        this.finishLoading();
      }
    });
  }

  private loadObligations(): void {
    this.reportsService.getObligationStats(
    this.startDate || undefined,
    this.endDate || undefined
    ).subscribe({
      next: (data) => {
        this.obligationStats = data;
        this.finishLoading();
      },
      error: (error) => {
        console.error('Obligation report error:', error);
        this.errorMessage = 'Unable to load the obligation report.';
        this.finishLoading();
      }
    });
  }

  private loadRenewals(): void {
    this.reportsService.getRenewalStats(
      this.startDate || undefined,
      this.endDate || undefined
    ).subscribe({
      next: (data) => {
        this.renewalStats = data;
        this.finishLoading();
      },
      error: (error) => {
        console.error('Renewal report error:', error);
        this.errorMessage = 'Unable to load the renewal report.';
        this.finishLoading();
      }
    });
  }

  private loadCompliance(): void {
    this.reportsService.getComplianceStats(
      this.startDate || undefined,
      this.endDate || undefined
    ).subscribe({
      next: (data) => {
        this.complianceStats = data;
        this.finishLoading();
      },
      error: (error) => {
        console.error('Compliance report error:', error);
        this.errorMessage = 'Unable to load the compliance report.';
        this.finishLoading();
      }
    });
  }

  private loadAllReports(): void {
    let completed = 0;
    let failed = false;

    const complete = (): void => {
      completed++;

      if (completed === 5) {
        this.loading = false;

        if (failed) {
          this.errorMessage = 'Unable to load one or more reports.';
        }

        this.cdr.detectChanges();
      }
    };

    this.reportsService.getContractStats(
      this.startDate || undefined,
      this.endDate || undefined
    ).subscribe({
      next: (data) => {
        this.contractStats = data;
        complete();
      },
      error: (error) => {
        console.error('Contract report error:', error);
        failed = true;
        complete();
      }
    });

    this.reportsService.getObligationStats(
      this.startDate || undefined,
      this.endDate || undefined
    ).subscribe({
      next: (data) => {
        this.obligationStats = data;
        complete();
      },
      error: (error) => {
        console.error('Obligation report error:', error);
        failed = true;
        complete();
      }
    });

    this.reportsService.getRenewalStats(
      this.startDate || undefined,
      this.endDate || undefined
    ).subscribe({
      next: (data) => {
        this.renewalStats = data;
        complete();
      },
      error: (error) => {
        console.error('Renewal report error:', error);
        failed = true;
        complete();
      }
    });

    this.reportsService.getComplianceStats(
      this.startDate || undefined,
      this.endDate || undefined
    ).subscribe({
      next: (data) => {
        this.complianceStats = data;
        complete();
      },
      error: (error) => {
        console.error('Compliance report error:', error);
        failed = true;
        complete();
      }
    });

    this.reportsService.getRiskSummary().subscribe({
      next: (data) => {
        this.riskSummary = data;
        complete();
      },
      error: (error) => {
        console.error('Risk report error:', error);
        failed = true;
        complete();
      }
    });
  }

  private finishLoading(): void {
    this.loading = false;
    this.cdr.detectChanges();
  }

  applyFilters(): void {
    if (this.startDate && this.endDate && this.startDate > this.endDate) {
      this.errorMessage = 'Start date cannot be later than end date.';
      this.successMessage = '';
      return;
    }

    this.loadReports();
  }

  clearFilters(): void {
    this.selectedReportType = 'all';
    this.startDate = '';
    this.endDate = '';
    this.loadReports();
  }

  getCategoryEntries(): { category: string; count: number }[] {
    if (!this.contractStats) {
      return [];
    }

    return Object.entries(this.contractStats.by_category).map(
      ([category, count]) => ({
        category,
        count
      })
    );
  }

  getRiskCount(): number {
    return this.riskSummary?.contracts_needing_attention.length || 0;
  }

  downloadFile(
    fileType: 'pdf' | 'excel',
    reportType: 'contracts' | 'obligations' | 'renewals' | 'compliance'
  ): void {

    let request$;

    if (reportType === 'contracts') {
      request$ = fileType === 'pdf'
        ? this.reportsService.exportContractsPdf()
        : this.reportsService.exportContractsExcel();

    } else if (reportType === 'obligations') {
      request$ = fileType === 'pdf'
        ? this.reportsService.exportObligationsPdf()
        : this.reportsService.exportObligationsExcel();

    } else if (reportType === 'renewals') {
      request$ = fileType === 'pdf'
        ? this.reportsService.exportRenewalsPdf()
        : this.reportsService.exportRenewalsExcel();

    } else {
      request$ = fileType === 'pdf'
        ? this.reportsService.exportCompliancePdf()
        : this.reportsService.exportComplianceExcel();
    }

    request$.subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');

        link.href = url;
        link.download =
          `${reportType}_report.${fileType === 'pdf' ? 'pdf' : 'xlsx'}`;

        link.click();
        window.URL.revokeObjectURL(url);

        this.successMessage =
          `${reportType} ${fileType.toUpperCase()} report downloaded.`;

        this.errorMessage = '';
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Report download error:', error);

        this.errorMessage =
          `Unable to download the ${reportType} ${fileType.toUpperCase()} report.`;

        this.successMessage = '';
        this.cdr.detectChanges();
      }
    });
  }
}
