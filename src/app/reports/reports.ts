import {
  Component,
  ChangeDetectorRef
} from '@angular/core';

import { CommonModule } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { ReportService } from '../services/report';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './reports.html',
  styleUrl: './reports.css'
})
export class Reports {

  // =========================================================
  // CONTRACT REPORT
  // =========================================================

  contracts: any[] = [];
  showContracts = false;
  loadingContracts = false;

  // =========================================================
  // OBLIGATION REPORT
  // =========================================================

  obligations: any[] = [];
  showObligations = false;
  loadingObligations = false;

  // =========================================================
  // RENEWAL REPORT
  // =========================================================

  renewals: any[] = [];
  showRenewals = false;
  loadingRenewals = false;

  // =========================================================
  // COMPLIANCE REPORT
  // =========================================================

  compliance: any[] = [];
  showCompliance = false;
  loadingCompliance = false;

  constructor(
    private readonly reportService: ReportService,
    private readonly cdr: ChangeDetectorRef
  ) {}

  // =========================================================
  // CONTRACT REPORT
  // =========================================================

  viewContractReport(): void {

    console.log('Contract Report: loading started');

    this.loadingContracts = true;
    this.showContracts = false;

    this.cdr.detectChanges();

    this.reportService.getContractsReport().subscribe({

      next: (data) => {

        console.log(
          'Contract Report received:',
          data
        );

        this.contracts = data ?? [];

        this.showContracts = true;
        this.loadingContracts = false;

        this.cdr.detectChanges();

        console.log(
          'Contract Report: loading finished'
        );
      },

      error: (error) => {

        console.error(
          'Contract Report error:',
          error
        );

        this.contracts = [];
        this.showContracts = false;
        this.loadingContracts = false;

        this.cdr.detectChanges();

        alert(
          'Unable to load Contract Report.'
        );
      }

    });
  }

  // =========================================================
  // OBLIGATION REPORT
  // =========================================================

  viewObligationReport(): void {

    console.log(
      'Obligation Report: loading started'
    );

    this.loadingObligations = true;
    this.showObligations = false;

    this.cdr.detectChanges();

    this.reportService
      .getObligationsReport()
      .subscribe({

        next: (data) => {

          console.log(
            'Obligation Report received:',
            data
          );

          this.obligations = data ?? [];

          this.showObligations = true;
          this.loadingObligations = false;

          this.cdr.detectChanges();

          console.log(
            'Obligation Report: loading finished'
          );
        },

        error: (error) => {

          console.error(
            'Obligation Report error:',
            error
          );

          this.obligations = [];
          this.showObligations = false;
          this.loadingObligations = false;

          this.cdr.detectChanges();

          alert(
            'Unable to load Obligation Report.'
          );
        }

      });
  }

  // =========================================================
  // RENEWAL REPORT
  // =========================================================

  viewRenewalReport(): void {

    console.log(
      'Renewal Report: loading started'
    );

    this.loadingRenewals = true;
    this.showRenewals = false;

    this.cdr.detectChanges();

    this.reportService
      .getRenewalsReport()
      .subscribe({

        next: (data) => {

          console.log(
            'Renewal Report received:',
            data
          );

          this.renewals = data ?? [];

          this.showRenewals = true;
          this.loadingRenewals = false;

          this.cdr.detectChanges();

          console.log(
            'Renewal Report: loading finished'
          );
        },

        error: (error) => {

          console.error(
            'Renewal Report error:',
            error
          );

          this.renewals = [];
          this.showRenewals = false;
          this.loadingRenewals = false;

          this.cdr.detectChanges();

          alert(
            'Unable to load Renewal Report.'
          );
        }

      });
  }

  // =========================================================
  // COMPLIANCE REPORT
  // =========================================================

  viewComplianceReport(): void {

    console.log(
      'Compliance Report: loading started'
    );

    this.loadingCompliance = true;
    this.showCompliance = false;

    this.cdr.detectChanges();

    this.reportService
      .getComplianceReport()
      .subscribe({

        next: (data) => {

          console.log(
            'Compliance Report received:',
            data
          );

          this.compliance = data ?? [];

          this.showCompliance = true;
          this.loadingCompliance = false;

          this.cdr.detectChanges();

          console.log(
            'Compliance Report: loading finished'
          );
        },

        error: (error) => {

          console.error(
            'Compliance Report error:',
            error
          );

          this.compliance = [];
          this.showCompliance = false;
          this.loadingCompliance = false;

          this.cdr.detectChanges();

          alert(
            'Unable to load Compliance Report.'
          );
        }

      });
  }

  // =========================================================
  // EXCEL DOWNLOADS
  // =========================================================

  downloadContractExcel(): void {

    this.reportService
      .downloadContractsExcel()
      .subscribe({

        next: (file) => {

          this.downloadFile(
            file,
            'contract-report.xlsx'
          );
        },

        error: (error) => {

          console.error(
            'Contract Excel download error:',
            error
          );

          alert(
            'Unable to download Contract Excel report.'
          );
        }

      });
  }

  downloadObligationExcel(): void {

    this.reportService
      .downloadObligationsExcel()
      .subscribe({

        next: (file) => {

          this.downloadFile(
            file,
            'obligation-report.xlsx'
          );
        },

        error: (error) => {

          console.error(
            'Obligation Excel download error:',
            error
          );

          alert(
            'Unable to download Obligation Excel report.'
          );
        }

      });
  }

  downloadRenewalExcel(): void {

    this.reportService
      .downloadRenewalsExcel()
      .subscribe({

        next: (file) => {

          this.downloadFile(
            file,
            'renewal-report.xlsx'
          );
        },

        error: (error) => {

          console.error(
            'Renewal Excel download error:',
            error
          );

          alert(
            'Unable to download Renewal Excel report.'
          );
        }

      });
  }

  downloadComplianceExcel(): void {

    this.reportService
      .downloadComplianceExcel()
      .subscribe({

        next: (file) => {

          this.downloadFile(
            file,
            'compliance-report.xlsx'
          );
        },

        error: (error) => {

          console.error(
            'Compliance Excel download error:',
            error
          );

          alert(
            'Unable to download Compliance Excel report.'
          );
        }

      });
  }

  // =========================================================
  // FILE DOWNLOAD HELPER
  // =========================================================

  private downloadFile(
    file: Blob,
    filename: string
  ): void {

    const url =
      window.URL.createObjectURL(file);

    const link =
      document.createElement('a');

    link.href = url;
    link.download = filename;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);
  }
}