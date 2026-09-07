import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

import { ReportService } from '../services/report';

@Component({
  selector: 'app-reports',
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule
  ],
  templateUrl: './reports.html',
  styleUrl: './reports.css'
})
export class Reports {

  // =====================================================
  // CONTRACT REPORT DATA
  // =====================================================

  contracts: any[] = [];
  showContracts = false;
  loadingContracts = false;

  // =====================================================
  // OBLIGATION REPORT DATA
  // =====================================================

  obligations: any[] = [];
  showObligations = false;
  loadingObligations = false;

  // =====================================================
  // RENEWAL REPORT DATA
  // =====================================================

  renewals: any[] = [];
  showRenewals = false;
  loadingRenewals = false;

  // =====================================================
  // COMPLIANCE REPORT DATA
  // =====================================================

  compliance: any[] = [];
  showCompliance = false;
  loadingCompliance = false;

  constructor(
    private reportService: ReportService
  ) {}

  // =====================================================
  // CONTRACT REPORT
  // =====================================================

  viewContractReport() {

    this.loadingContracts = true;

    this.reportService.getContractsReport().subscribe({

      next: (data) => {

        this.contracts = data;
        this.showContracts = true;
        this.loadingContracts = false;

      },

      error: (error) => {

        console.error(
          'Contract report error:',
          error
        );

        this.loadingContracts = false;

        alert(
          'Unable to load Contract Report. Please check whether the backend is running.'
        );

      }

    });
  }

  // =====================================================
  // OBLIGATION REPORT
  // =====================================================

  viewObligationReport() {

    this.loadingObligations = true;

    this.reportService.getObligationsReport().subscribe({

      next: (data) => {

        this.obligations = data;
        this.showObligations = true;
        this.loadingObligations = false;

      },

      error: (error) => {

        console.error(
          'Obligation report error:',
          error
        );

        this.loadingObligations = false;

        alert(
          'Unable to load Obligation Report. Please check whether the backend is running.'
        );

      }

    });
  }

  // =====================================================
  // RENEWAL REPORT
  // =====================================================

  viewRenewalReport() {

    this.loadingRenewals = true;

    this.reportService.getRenewalsReport().subscribe({

      next: (data) => {

        this.renewals = data;
        this.showRenewals = true;
        this.loadingRenewals = false;

      },

      error: (error) => {

        console.error(
          'Renewal report error:',
          error
        );

        this.loadingRenewals = false;

        alert(
          'Unable to load Renewal Report. Please check whether the backend is running.'
        );

      }

    });
  }

  // =====================================================
  // COMPLIANCE REPORT
  // =====================================================

  viewComplianceReport() {

    this.loadingCompliance = true;

    this.reportService.getComplianceReport().subscribe({

      next: (data) => {

        this.compliance = data;
        this.showCompliance = true;
        this.loadingCompliance = false;

      },

      error: (error) => {

        console.error(
          'Compliance report error:',
          error
        );

        this.loadingCompliance = false;

        alert(
          'Unable to load Compliance Report. Please check whether the backend is running.'
        );

      }

    });
  }


  // =====================================================
  // DOWNLOAD CONTRACT EXCEL
  // =====================================================

  downloadContractExcel() {

    this.reportService.downloadContractsExcel().subscribe({

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


  // =====================================================
  // DOWNLOAD OBLIGATION EXCEL
  // =====================================================

  downloadObligationExcel() {

    this.reportService.downloadObligationsExcel().subscribe({

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


  // =====================================================
  // DOWNLOAD RENEWAL EXCEL
  // =====================================================

  downloadRenewalExcel() {

    this.reportService.downloadRenewalsExcel().subscribe({

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


  // =====================================================
  // DOWNLOAD COMPLIANCE EXCEL
  // =====================================================

  downloadComplianceExcel() {

    this.reportService.downloadComplianceExcel().subscribe({

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


  // =====================================================
  // COMMON FILE DOWNLOAD FUNCTION
  // =====================================================

  private downloadFile(
    file: Blob,
    filename: string
  ) {

    const url = window.URL.createObjectURL(file);

    const link = document.createElement('a');

    link.href = url;

    link.download = filename;

    link.click();

    window.URL.revokeObjectURL(url);
  }

}