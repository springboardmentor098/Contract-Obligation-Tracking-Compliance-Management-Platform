import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { forkJoin } from 'rxjs';
import {
  ContractAnalytics,
  DashboardSummary,
  ObligationAnalytics,
  RenewalAnalytics,
  ReportService
} from '../../core/services/report.service';

interface ReportRow {
  name: string;
  value: number;
}

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reports.html',
  styleUrl: './reports.scss'
})
export class Reports implements OnInit {
  private readonly reportService = inject(ReportService);
  private readonly cdr = inject(ChangeDetectorRef);

  summary: DashboardSummary | null = null;
  contracts: ContractAnalytics | null = null;
  obligations: ObligationAnalytics | null = null;
  renewals: RenewalAnalytics | null = null;
  compliance: any = null;

  loading = true;
  error = '';
  exporting = '';

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports(): void {
    this.loading = true;
    this.error = '';

    forkJoin({
      summary: this.reportService.getDashboardSummary(),
      contracts: this.reportService.getContractAnalytics(),
      obligations: this.reportService.getObligationAnalytics(),
      renewals: this.reportService.getRenewalAnalytics(),
      compliance: this.reportService.getComplianceAnalytics()
    }).subscribe({
      next: (result) => {
        this.summary = result.summary;
        this.contracts = result.contracts.contracts;

        let obligationData = result.obligations;

        // Backend may return the obligation analytics
        // as a JSON string instead of an object.
        if (typeof obligationData === 'string') {
          try {
            obligationData = JSON.parse(obligationData);
          } catch {
            console.error('Unable to parse obligation analytics');
          }
        }

        this.obligations =
          obligationData?.obligations ?? obligationData;

        this.renewals = result.renewals.renewals;
        this.compliance = result.compliance.compliance;

        this.loading = false;
        this.cdr.detectChanges();
      },

      error: (err) => {
        console.error('Reports loading error:', err);
        this.error = 'Unable to load reports and analytics.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  objectToRows(data: Record<string, number> | null | undefined): ReportRow[] {
    if (!data) return [];

    return Object.entries(data)
      .map(([name, value]) => ({
        name,
        value
      }))
      .sort((a, b) => b.value - a.value);
  }

  getMaxValue(data: Record<string, number> | null | undefined): number {
    const rows = this.objectToRows(data);
    return rows.length ? Math.max(...rows.map(row => row.value)) : 1;
  }

  getBarWidth(
    value: number,
    data: Record<string, number> | null | undefined
  ): number {
    const max = this.getMaxValue(data);
    return max ? (value / max) * 100 : 0;
  }

  downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');

    anchor.href = url;
    anchor.download = filename;
    anchor.click();

    window.URL.revokeObjectURL(url);
  }

  export(type: string): void {
    this.exporting = type;

    let request;

    switch (type) {
      case 'contracts-excel':
        request = this.reportService.exportContractsExcel();
        break;

      case 'contracts-pdf':
        request = this.reportService.exportContractsPdf();
        break;

      case 'obligations-excel':
        request = this.reportService.exportObligationsExcel();
        break;

      case 'renewals-excel':
        request = this.reportService.exportRenewalsExcel();
        break;

      case 'dashboard-pdf':
        request = this.reportService.exportDashboardPdf();
        break;

      default:
        this.exporting = '';
        return;
    }

    request.subscribe({
      next: (blob) => {
        const extension =
          type.endsWith('pdf') ? 'pdf' : 'xlsx';

        this.downloadBlob(
          blob,
          `contractiq-${type}.${extension}`
        );

        this.exporting = '';
        this.cdr.detectChanges();
      },

      error: (err) => {
        console.error('Export error:', err);
        this.error = `Unable to export ${type}.`;
        this.exporting = '';
        this.cdr.detectChanges();
      }
    });
  }
}
