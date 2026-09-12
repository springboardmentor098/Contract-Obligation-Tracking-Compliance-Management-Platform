import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import {
  ReportService,
  ContractSummary,
  ObligationSummary,
  RenewalSummary,
  ComplianceSummary,
  RiskSummary
} from '../services/report';


@Component({
  selector: 'app-reports',
  standalone: true,

  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ],

  templateUrl: './reports.html',
  styleUrl: './reports.less'
})


export class Reports implements OnInit {

  // =====================================================
  // DATA
  // =====================================================

  contractSummary: ContractSummary | null = null;

  obligationSummary: ObligationSummary | null = null;

  renewalSummary: RenewalSummary | null = null;

  complianceSummary: ComplianceSummary | null = null;

  riskData: RiskSummary[] = [];


  // =====================================================
  // UI STATE
  // =====================================================

  loading = true;

  errorMessage = '';

  downloading = '';


  // =====================================================
  // CONSTRUCTOR
  // =====================================================

  constructor(
    private reportService: ReportService,
    private cdr: ChangeDetectorRef
  ) {}


  // =====================================================
  // INIT
  // =====================================================

  ngOnInit(): void {

    this.loadReports();

  }


  // =====================================================
  // LOAD REPORTS
  // =====================================================

  loadReports(): void {

    this.loading = true;

    this.errorMessage = '';

    this.contractSummary = null;
    this.obligationSummary = null;
    this.renewalSummary = null;
    this.complianceSummary = null;
    this.riskData = [];

    this.cdr.detectChanges();


    // -----------------------------------------------------
    // CONTRACT SUMMARY
    // -----------------------------------------------------

    this.reportService.getContractSummary().subscribe({

      next: (data) => {

        console.log(
          'Contract Summary:',
          data
        );

        this.contractSummary = data;

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Contract Summary Error:',
          error
        );

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });


    // -----------------------------------------------------
    // OBLIGATION SUMMARY
    // -----------------------------------------------------

    this.reportService.getObligationSummary().subscribe({

      next: (data) => {

        console.log(
          'Obligation Summary:',
          data
        );

        this.obligationSummary = data;

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Obligation Summary Error:',
          error
        );

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });


    // -----------------------------------------------------
    // RENEWAL SUMMARY
    // -----------------------------------------------------

    this.reportService.getRenewalSummary().subscribe({

      next: (data) => {

        console.log(
          'Renewal Summary:',
          data
        );

        this.renewalSummary = data;

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Renewal Summary Error:',
          error
        );

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });


    // -----------------------------------------------------
    // COMPLIANCE SUMMARY
    // -----------------------------------------------------

    this.reportService.getComplianceSummary().subscribe({

      next: (data) => {

        console.log(
          'Compliance Summary:',
          data
        );

        this.complianceSummary = data;

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Compliance Summary Error:',
          error
        );

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });


    // -----------------------------------------------------
    // RISK REPORT
    // -----------------------------------------------------

    this.reportService.getRiskReport().subscribe({

      next: (data) => {

        console.log(
          'Risk Report:',
          data
        );

        this.riskData = data || [];

        this.loading = false;

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Risk Report Error:',
          error
        );

        this.riskData = [];

        this.loading = false;

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });

  }


  // =====================================================
  // ERROR HANDLING
  // =====================================================

  handleError(error: any): void {

    if (this.errorMessage) {
      return;
    }


    if (error?.status === 401) {

      this.errorMessage =
        'Your session has expired. Please login again.';

    }

    else if (error?.status === 403) {

      this.errorMessage =
        'You are not authorized to view reports.';

    }

    else if (error?.status === 0) {

      this.errorMessage =
        'Unable to connect to the backend server.';

    }

    else {

      this.errorMessage =
        'Failed to load reports. Please try again.';

    }

  }


  // =====================================================
  // REFRESH
  // =====================================================

  refresh(): void {

    this.loadReports();

  }


  // =====================================================
  // RETRY
  // =====================================================

  retry(): void {

    this.loadReports();

  }


  // =====================================================
  // CONTRACT STATUS
  // =====================================================

  getStatusClass(status: string): string {

    switch (status) {

      case 'Active':
        return 'active';

      case 'Draft':
        return 'draft';

      case 'Under Review':
        return 'under-review';

      case 'Approved':
        return 'approved';

      case 'Expired':
        return 'expired';

      case 'Terminated':
        return 'terminated';

      default:
        return 'default';

    }

  }


  // =====================================================
  // OBLIGATION STATUS
  // =====================================================

  getObligationStatusClass(status: string): string {

    switch (status) {

      case 'Pending':
        return 'pending';

      case 'In Progress':
        return 'in-progress';

      case 'Completed':
        return 'completed';

      case 'Delayed':
        return 'delayed';

      case 'Overdue':
        return 'overdue';

      default:
        return 'default';

    }

  }


  // =====================================================
  // COMPLIANCE SCORE
  // =====================================================

  getScoreClass(score: number): string {

    if (score >= 80) {
      return 'good';
    }

    if (score >= 50) {
      return 'medium';
    }

    return 'poor';

  }


  // =====================================================
  // RISK CLASS
  // =====================================================

  getRiskClass(risk: string): string {

    switch (risk) {

      case 'High':
        return 'high';

      case 'Medium':
        return 'medium';

      case 'Low':
        return 'low';

      default:
        return 'default';

    }

  }


  // =====================================================
  // GENERIC FILE SAVE
  // =====================================================

  private saveFile(
    blob: Blob,
    filename: string
  ): void {

    const url =
      window.URL.createObjectURL(blob);

    const link =
      document.createElement('a');

    link.href = url;

    link.download = filename;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);

  }


  // =====================================================
  // CONTRACT PDF
  // =====================================================

  downloadContractPdf(): void {

    this.downloading = 'contract-pdf';

    this.cdr.detectChanges();


    this.reportService.downloadContractPdf().subscribe({

      next: (blob) => {

        this.saveFile(
          blob,
          'contract_report.pdf'
        );

        this.downloading = '';

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Contract PDF Error:',
          error
        );

        this.downloading = '';

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });

  }


  // =====================================================
  // CONTRACT EXCEL
  // =====================================================

  downloadContractExcel(): void {

    this.downloading = 'contract-excel';

    this.cdr.detectChanges();


    this.reportService.downloadContractExcel().subscribe({

      next: (blob) => {

        this.saveFile(
          blob,
          'contract_report.xlsx'
        );

        this.downloading = '';

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Contract Excel Error:',
          error
        );

        this.downloading = '';

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });

  }


  // =====================================================
  // OBLIGATION PDF
  // =====================================================

  downloadObligationPdf(): void {

    this.downloading = 'obligation-pdf';

    this.cdr.detectChanges();


    this.reportService.downloadObligationPdf().subscribe({

      next: (blob) => {

        this.saveFile(
          blob,
          'obligation_report.pdf'
        );

        this.downloading = '';

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Obligation PDF Error:',
          error
        );

        this.downloading = '';

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });

  }


  // =====================================================
  // OBLIGATION EXCEL
  // =====================================================

  downloadObligationExcel(): void {

    this.downloading = 'obligation-excel';

    this.cdr.detectChanges();


    this.reportService.downloadObligationExcel().subscribe({

      next: (blob) => {

        this.saveFile(
          blob,
          'obligation_report.xlsx'
        );

        this.downloading = '';

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Obligation Excel Error:',
          error
        );

        this.downloading = '';

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });

  }


  // =====================================================
  // RENEWAL PDF
  // =====================================================

  downloadRenewalPdf(): void {

    this.downloading = 'renewal-pdf';

    this.cdr.detectChanges();


    this.reportService.downloadRenewalPdf().subscribe({

      next: (blob) => {

        this.saveFile(
          blob,
          'renewal_report.pdf'
        );

        this.downloading = '';

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Renewal PDF Error:',
          error
        );

        this.downloading = '';

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });

  }


  // =====================================================
  // RENEWAL EXCEL
  // =====================================================

  downloadRenewalExcel(): void {

    this.downloading = 'renewal-excel';

    this.cdr.detectChanges();


    this.reportService.downloadRenewalExcel().subscribe({

      next: (blob) => {

        this.saveFile(
          blob,
          'renewal_report.xlsx'
        );

        this.downloading = '';

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Renewal Excel Error:',
          error
        );

        this.downloading = '';

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });

  }


  // =====================================================
  // COMPLIANCE PDF
  // =====================================================

  downloadCompliancePdf(): void {

    this.downloading = 'compliance-pdf';

    this.cdr.detectChanges();


    this.reportService.downloadCompliancePdf().subscribe({

      next: (blob) => {

        this.saveFile(
          blob,
          'compliance_report.pdf'
        );

        this.downloading = '';

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Compliance PDF Error:',
          error
        );

        this.downloading = '';

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });

  }


  // =====================================================
  // COMPLIANCE EXCEL
  // =====================================================

  downloadComplianceExcel(): void {

    this.downloading = 'compliance-excel';

    this.cdr.detectChanges();


    this.reportService.downloadComplianceExcel().subscribe({

      next: (blob) => {

        this.saveFile(
          blob,
          'compliance_report.xlsx'
        );

        this.downloading = '';

        this.cdr.detectChanges();

      },

      error: (error) => {

        console.error(
          'Compliance Excel Error:',
          error
        );

        this.downloading = '';

        this.handleError(error);

        this.cdr.detectChanges();

      }

    });

  }

}