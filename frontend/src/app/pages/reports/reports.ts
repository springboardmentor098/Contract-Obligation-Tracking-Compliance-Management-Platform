import { Component, OnInit, inject } from '@angular/core';
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

  constructor() {
    console.log('🔥🔥🔥 REPORTS COMPONENT LOADED 🔥🔥🔥');
  }

  loading = true;
  error = '';
  downloading = '';

  dashboard: any = null;
  contracts: any = null;
  obligations: any = null;
  renewals: any = null;
  compliance: any = null;
  risks: any[] = [];

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports(): void {
    this.loading = true;
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
        this.dashboard = data.dashboard;
        this.contracts = data.contracts;
        this.obligations = data.obligations;
        this.renewals = data.renewals;
        this.compliance = data.compliance;
        this.risks = Array.isArray(data.risks) ? data.risks : [];

        this.loading = false;
      },
      error: (err) => {
        console.error('Reports loading error:', err);

        this.loading = false;
        this.error = this.getErrorMessage(err);
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
        console.error('Download error:', err);

        this.downloading = '';
        this.error = `Unable to download the ${type} ${format} report.`;
      }
    });
  }

  isDownloading(type: string, format: 'pdf' | 'excel'): boolean {
    return this.downloading === `${type}-${format}`;
  }

  private getErrorMessage(err: any): string {
    if (err?.status === 401) {
      return 'Your session has expired. Please sign in again.';
    }

    if (err?.status === 403) {
      return 'You do not have permission to view these reports.';
    }

    return 'Unable to load reports. Please check the backend connection and try again.';
  }
}
