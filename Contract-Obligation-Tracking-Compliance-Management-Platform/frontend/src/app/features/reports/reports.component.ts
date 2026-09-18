import { Component, inject } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';

import { DashboardService } from '../../core/services/dashboard.service';

import {
  ReportService,
  ContractReport,
  ObligationReport,
  RenewalReport,
  ComplianceReport
} from '../../core/services/report.service';

import { DashboardSummary } from '../../core/models/models';

import { PageHeaderComponent } from '../../shared/page-header.component';


type ReportType =
  | 'contracts'
  | 'obligations'
  | 'renewals'
  | 'compliance';


@Component({
  selector: 'cq-reports',
  standalone: true,

  imports: [
    CommonModule,
    DecimalPipe,
    PageHeaderComponent
  ],

  templateUrl: './reports.component.html',
  styleUrl: './reports.component.css'
})
export class ReportsComponent {

  private readonly dashboard =
    inject(DashboardService);

  private readonly reports =
    inject(ReportService);


  // ==========================================================
  // ANALYTICS
  // ==========================================================

  data?: DashboardSummary;

  loading = true;

  error = '';


  // ==========================================================
  // REPORT STATE
  // ==========================================================

  reportsLoading = false;

  reportError = '';

  selectedReport: ReportType | null = null;


  // ==========================================================
  // REPORT DATA
  // ==========================================================

  contractReport?: ContractReport;

  obligationReport?: ObligationReport;

  renewalReport?: RenewalReport;

  complianceReport?: ComplianceReport;


  // ==========================================================
  // INIT
  // ==========================================================

  constructor() {

    this.load();

  }


  // ==========================================================
  // LOAD ANALYTICS
  // ==========================================================

  load(): void {

    this.loading = true;

    this.error = '';

    this.dashboard
      .getSummary()
      .subscribe({

        next: (result) => {

          this.data = result;

          this.loading = false;

        },

        error: (err) => {

          this.error =
            err?.error?.detail ||
            'Unable to load analytics.';

          this.loading = false;

        }

      });

  }


  // ==========================================================
  // REFRESH
  // ==========================================================

  refresh(): void {

    this.load();

    if (this.selectedReport) {

      this.loadReport(
        this.selectedReport
      );

    }

  }


  // ==========================================================
  // VIEW REPORT
  // ==========================================================

  viewReport(
    report: ReportType
  ): void {

    this.selectedReport = report;

    this.reportError = '';

    this.loadReport(report);

  }


  // ==========================================================
  // LOAD REAL REPORT FROM FASTAPI
  // ==========================================================

  private loadReport(
    report: ReportType
  ): void {

    this.reportsLoading = true;

    this.reportError = '';


    if (report === 'contracts') {

      this.reports
        .contracts()
        .subscribe({

          next: (data) => {

            this.contractReport = data;

            this.reportsLoading = false;

          },

          error: (err) => {

            this.handleReportError(
              err
            );

          }

        });

      return;

    }


    if (report === 'obligations') {

      this.reports
        .obligations()
        .subscribe({

          next: (data) => {

            this.obligationReport = data;

            this.reportsLoading = false;

          },

          error: (err) => {

            this.handleReportError(
              err
            );

          }

        });

      return;

    }


    if (report === 'renewals') {

      this.reports
        .renewals()
        .subscribe({

          next: (data) => {

            this.renewalReport = data;

            this.reportsLoading = false;

          },

          error: (err) => {

            this.handleReportError(
              err
            );

          }

        });

      return;

    }


    if (report === 'compliance') {

      this.reports
        .compliance()
        .subscribe({

          next: (data) => {

            this.complianceReport = data;

            this.reportsLoading = false;

          },

          error: (err) => {

            this.handleReportError(
              err
            );

          }

        });

      return;

    }

  }


  // ==========================================================
  // ERROR
  // ==========================================================

  private handleReportError(
    err: any
  ): void {

    console.error(
      'Report loading error:',
      err
    );

    this.reportsLoading = false;

    this.reportError =
      err?.error?.detail ||
      'Unable to load the selected report.';

  }


  // ==========================================================
  // CLOSE
  // ==========================================================

  closeReport(): void {

    this.selectedReport = null;

    this.reportError = '';

  }


  // ==========================================================
  // REPORT TITLE
  // ==========================================================

  getReportTitle(): string {

    switch (
      this.selectedReport
    ) {

      case 'contracts':
        return 'Contract Report';

      case 'obligations':
        return 'Obligation Report';

      case 'renewals':
        return 'Renewal Report';

      case 'compliance':
        return 'Compliance Report';

      default:
        return 'ContractIQ Report';

    }

  }


  // ==========================================================
  // PRINT
  // ==========================================================

  printReport(
    report: ReportType | null
  ): void {

    if (!report) {
      return;
    }


    if (
      this.selectedReport !== report
    ) {

      this.selectedReport = report;

      this.loadReport(report);

    }


    setTimeout(() => {

      window.print();

    }, 500);

  }


  // ==========================================================
  // ANALYTICS HELPERS
  // ==========================================================

  entries(
    value:
      Record<string, number>
      | undefined
  ): [string, number][] {

    return Object.entries(
      value ?? {}
    );

  }


  total(
    value:
      Record<string, number>
      | undefined
  ): number {

    return Object.values(
      value ?? {}
    ).reduce(
      (
        sum,
        current
      ) => sum + current,
      0
    );

  }

}
