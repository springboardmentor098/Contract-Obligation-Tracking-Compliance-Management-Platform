import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { forkJoin } from 'rxjs';
import { Api } from '../../services/api';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reports.html',
  styleUrl: './reports.scss',
})
export class Reports implements OnInit {
  private api = inject(Api);
  private cdr = inject(ChangeDetectorRef);

  loading = false;
  refreshing = false;
  error = '';
  downloading = '';

  dashboard: any = null;
  contracts: any = null;
  obligations: any = null;
  renewals: any = null;
  compliance: any = null;
  risks: any[] = [];

  ngOnInit(): void {
    this.loadReports(true);
  }

  loadReports(initialLoad = false): void {
    console.log('📊 REPORTS: starting load', { initialLoad });

    if (initialLoad) {
      this.loading = true;
    } else {
      this.refreshing = true;
    }

    this.error = '';

    forkJoin({
      dashboard: this.api.getDashboardSummary(),
      contracts: this.api.getContractSummary(),
      obligations: this.api.getObligationSummary(),
      renewals: this.api.getRenewalSummary(),
      compliance: this.api.getComplianceSummary(),
      risks: this.api.getRiskReport()
    }).subscribe({
      next: (data) => {
        console.log('📊 REPORTS: DATA RECEIVED', data);

        this.dashboard = data.dashboard;
        this.contracts = data.contracts;
        this.obligations = data.obligations;
        this.renewals = data.renewals;
        this.compliance = data.compliance;
        this.risks = Array.isArray(data.risks) ? data.risks : [];

        this.loading = false;
        this.refreshing = false;

        console.log('📊 REPORTS VALUES:', {
          contracts: this.contracts?.total,
          active: this.contracts?.active,
          obligations: this.obligations?.total,
          renewals: this.renewals?.upcoming,
          compliance: this.compliance?.average_score,
          risks: this.risks.length
        });

        this.cdr.detectChanges();

        console.log('📊 REPORTS: change detection completed');
      },

      error: (err) => {
        console.error('❌ REPORTS: API ERROR', err);

        this.loading = false;
        this.refreshing = false;
        this.error = this.getErrorMessage(err);

        this.cdr.detectChanges();
      }
    });
  }

  download(type: string, format: 'pdf' | 'excel'): void {
    const key = `${type}-${format}`;

    this.downloading = key;

    this.api.downloadReport(type, format).subscribe({
      next: (blob) => {
        const extension = format === 'pdf' ? 'pdf' : 'xlsx';
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');

        link.href = url;
        link.download = `${type}-report.${extension}`;
        link.click();

        window.URL.revokeObjectURL(url);
        this.downloading = '';
      },

      error: (err) => {
        console.error('❌ REPORT DOWNLOAD ERROR', err);
        this.downloading = '';
        this.error = this.getErrorMessage(err);
      }
    });
  }

  isDownloading(type: string, format: 'pdf' | 'excel'): boolean {
    return this.downloading === `${type}-${format}`;
  }

  private getErrorMessage(err: any): string {
    if (err?.error?.detail) {
      return err.error.detail;
    }

    if (err?.error?.message) {
      return err.error.message;
    }

    if (err?.message) {
      return err.message;
    }

    return 'Unable to load reports. Please try again.';
  }
}
