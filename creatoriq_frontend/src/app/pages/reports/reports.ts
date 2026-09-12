import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import {
  Reports as ReportsService,
  ContractReport,
  ObligationReport,
  RenewalReport,
  ComplianceReport
} from '../../services/reports';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [],
  templateUrl: './reports.html',
  styleUrl: './reports.css'
})
export class Reports implements OnInit {

  contractReport: ContractReport | null = null;
  obligationReport: ObligationReport | null = null;
  renewalReport: RenewalReport | null = null;
  complianceReport: ComplianceReport | null = null;

  loading = false;
  errorMessage = '';

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

    this.cdr.detectChanges();

    this.reportsService.getContractReport().subscribe({
      next: (data) => {
        console.log('Contract report received:', data);
        this.contractReport = data;
        this.loadObligationReport();
      },
      error: (error) => {
        this.handleError(error);
      }
    });
  }

  private loadObligationReport(): void {
    this.reportsService.getObligationReport().subscribe({
      next: (data) => {
        console.log('Obligation report received:', data);
        this.obligationReport = data;
        this.loadRenewalReport();
      },
      error: (error) => {
        this.handleError(error);
      }
    });
  }

  private loadRenewalReport(): void {
    this.reportsService.getRenewalReport().subscribe({
      next: (data) => {
        console.log('Renewal report received:', data);
        this.renewalReport = data;
        this.loadComplianceReport();
      },
      error: (error) => {
        this.handleError(error);
      }
    });
  }

  private loadComplianceReport(): void {
    this.reportsService.getComplianceReport().subscribe({
      next: (data) => {
        console.log('Compliance report received:', data);

        this.complianceReport = data;
        this.loading = false;

        console.log('All reports loaded successfully.');

        this.cdr.detectChanges();
      },
      error: (error) => {
        this.handleError(error);
      }
    });
  }

  private handleError(error: any): void {
    console.error('Reports API error:', error);

    this.loading = false;

    if (error.status === 401) {
      this.errorMessage = 'Your session has expired. Please log in again.';
    } else if (error.status === 403) {
      this.errorMessage = 'You do not have permission to view reports.';
    } else {
      this.errorMessage = 'Unable to load reports.';
    }

    this.cdr.detectChanges();
  }

  downloadContractPdf(): void {
    this.reportsService.downloadContractPdf().subscribe({
      next: (file) => this.saveFile(file, 'contract_report.pdf'),
      error: (error) => this.handleError(error)
    });
  }

  downloadContractExcel(): void {
    this.reportsService.downloadContractExcel().subscribe({
      next: (file) => this.saveFile(file, 'contract_report.xlsx'),
      error: (error) => this.handleError(error)
    });
  }

  downloadObligationPdf(): void {
    this.reportsService.downloadObligationPdf().subscribe({
      next: (file) => this.saveFile(file, 'obligation_report.pdf'),
      error: (error) => this.handleError(error)
    });
  }

  downloadObligationExcel(): void {
    this.reportsService.downloadObligationExcel().subscribe({
      next: (file) => this.saveFile(file, 'obligation_report.xlsx'),
      error: (error) => this.handleError(error)
    });
  }

  downloadRenewalPdf(): void {
    this.reportsService.downloadRenewalPdf().subscribe({
      next: (file) => this.saveFile(file, 'renewal_report.pdf'),
      error: (error) => this.handleError(error)
    });
  }

  downloadRenewalExcel(): void {
    this.reportsService.downloadRenewalExcel().subscribe({
      next: (file) => this.saveFile(file, 'renewal_report.xlsx'),
      error: (error) => this.handleError(error)
    });
  }

  downloadCompliancePdf(): void {
    this.reportsService.downloadCompliancePdf().subscribe({
      next: (file) => this.saveFile(file, 'compliance_report.pdf'),
      error: (error) => this.handleError(error)
    });
  }

  downloadComplianceExcel(): void {
    this.reportsService.downloadComplianceExcel().subscribe({
      next: (file) => this.saveFile(file, 'compliance_report.xlsx'),
      error: (error) => this.handleError(error)
    });
  }

  private saveFile(file: Blob, fileName: string): void {
    const url = window.URL.createObjectURL(file);
    const link = document.createElement('a');

    link.href = url;
    link.download = fileName;
    link.click();

    window.URL.revokeObjectURL(url);
  }
}