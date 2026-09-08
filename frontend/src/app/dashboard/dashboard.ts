import {
  Component,
  OnInit,
  ChangeDetectorRef
} from '@angular/core';

import { DashboardService } from '../services/dashboard.service';

import { Chart } from 'chart.js/auto';


@Component({
  selector: 'app-dashboard',
  imports: [],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})

export class Dashboard implements OnInit {

  // ===============================
  // DASHBOARD DATA
  // ===============================

  dashboardData: any = {

    contracts: {
      total: 0,
      active: 0,
      draft: 0,
      under_review: 0,
      approved: 0,
      expired: 0,
      terminated: 0
    },

    obligations: {
      total: 0,
      pending: 0,
      in_progress: 0,
      completed: 0,
      delayed: 0,
      overdue: 0
    },

    renewals: {
      upcoming: 0,
      in_progress: 0,
      renewed: 0,
      expired: 0,
      cancelled: 0
    },

    compliance: {
      compliant: 0,
      pending: 0,
      delayed: 0,
      non_compliant: 0,
      high_risk: 0
    }

  };


  // ===============================
  // UPCOMING EXPIRY DATA
  // ===============================

  upcomingExpiryContracts: any[] = [];
  // ===============================
// HIGH RISK CONTRACTS DATA
// ===============================

highRiskContracts: any[] = [];

  // ===============================
  // DEPARTMENT PERFORMANCE DATA
  // ===============================

  departmentPerformance: any[] = [];
  // ===============================
// OVERDUE OBLIGATIONS DATA
// ===============================

overdueObligations: any[] = [];


  // ===============================
  // UPCOMING RENEWALS DATA
  // ===============================

  upcomingRenewals: any[] = [];


  constructor(

    private dashboardService: DashboardService,

    private cdr: ChangeDetectorRef

  ) {}


  // ===============================
  // COMPONENT INITIALIZATION
  // ===============================

  ngOnInit(): void {

    console.log('Dashboard Component Loaded');

    this.loadDashboard();

    this.loadUpcomingExpiry();

    this.loadDepartmentPerformance();

    this.loadUpcomingRenewals();
    this.loadHighRiskContracts();
    this.loadOverdueObligations();

  }


  // ===============================
  // LOAD DASHBOARD
  // ===============================

  loadDashboard(): void {

    this.dashboardService
      .getDashboardSummary()
      .subscribe({

        next: (data: any) => {

          console.log('Dashboard Data:', data);

          this.dashboardData = data;

          this.cdr.detectChanges();

          this.createContractStatusChart();

          this.createObligationStatusChart();

          this.createComplianceStatusChart();

          this.createContractCategoryChart();

        },

        error: (error: any) => {

          console.error(
            'Error loading dashboard:',
            error
          );

        }

      });

  }


  // ===============================
  // LOAD UPCOMING EXPIRY
  // ===============================

  loadUpcomingExpiry(): void {

    this.dashboardService
      .getUpcomingExpiry()
      .subscribe({

        next: (data: any) => {

          console.log(
            'Upcoming Expiry Contracts:',
            data
          );

          this.upcomingExpiryContracts = data;

          this.cdr.detectChanges();

        },

        error: (error: any) => {

          console.error(
            'Error loading Upcoming Expiry:',
            error
          );

        }

      });

  }


  // ===============================
  // LOAD DEPARTMENT PERFORMANCE
  // ===============================

  loadDepartmentPerformance(): void {

    this.dashboardService
      .getDepartmentPerformance()
      .subscribe({

        next: (data: any) => {

          console.log(
            'Department Performance:',
            data
          );

          this.departmentPerformance = data;

          this.cdr.detectChanges();

          this.createDepartmentPerformanceChart();

        },

        error: (error: any) => {

          console.error(
            'Error loading Department Performance:',
            error
          );

        }

      });

  }


  // ===============================
  // LOAD UPCOMING RENEWALS
  // ===============================

  loadUpcomingRenewals(): void {

    this.dashboardService
      .getUpcomingRenewals()
      .subscribe({

        next: (data: any) => {

          console.log(
            'Upcoming Renewals:',
            data
          );

          this.upcomingRenewals = data;

          this.cdr.detectChanges();

        },

        error: (error: any) => {

          console.error(
            'Error loading Upcoming Renewals:',
            error
          );

        }

      });

  }


  // ===============================
  // CONTRACT STATUS CHART
  // ===============================

  createContractStatusChart(): void {

    new Chart('contractStatusChart', {

      type: 'bar',

      data: {

        labels: [

          'Draft',
          'Under Review',
          'Approved',
          'Active',
          'Expired',
          'Terminated'

        ],

        datasets: [

          {

            label: 'Contracts',

            data: [

              this.dashboardData.contracts.draft,

              this.dashboardData.contracts.under_review,

              this.dashboardData.contracts.approved,

              this.dashboardData.contracts.active,

              this.dashboardData.contracts.expired,

              this.dashboardData.contracts.terminated

            ]

          }

        ]

      },

      options: {

        responsive: true

      }

    });

  }


  // ===============================
  // OBLIGATION STATUS CHART
  // ===============================

  createObligationStatusChart(): void {

    new Chart('obligationStatusChart', {

      type: 'bar',

      data: {

        labels: [

          'Pending',
          'In Progress',
          'Completed',
          'Delayed',
          'Overdue'

        ],

        datasets: [

          {

            label: 'Obligations',

            data: [

              this.dashboardData.obligations.pending,

              this.dashboardData.obligations.in_progress,

              this.dashboardData.obligations.completed,

              this.dashboardData.obligations.delayed,

              this.dashboardData.obligations.overdue

            ]

          }

        ]

      },

      options: {

        responsive: true

      }

    });

  }


  // ===============================
  // COMPLIANCE STATUS CHART
  // ===============================

  createComplianceStatusChart(): void {

    new Chart('complianceStatusChart', {

      type: 'doughnut',

      data: {

        labels: [

          'Compliant',
          'Pending',
          'Delayed',
          'Non-Compliant',
          'High Risk'

        ],

        datasets: [

          {

            label: 'Compliance',

            data: [

              this.dashboardData.compliance.compliant,

              this.dashboardData.compliance.pending,

              this.dashboardData.compliance.delayed,

              this.dashboardData.compliance.non_compliant,

              this.dashboardData.compliance.high_risk

            ]

          }

        ]

      },

      options: {

        responsive: true

      }

    });

  }


  // ===============================
  // CONTRACT CATEGORY CHART
  // ===============================

  createContractCategoryChart(): void {

    this.dashboardService
      .getContractSummary()
      .subscribe({

        next: (data: any) => {

          console.log(
            'Contract Summary:',
            data
          );

          const categories = data.categories || {};


          new Chart('contractCategoryChart', {

            type: 'pie',

            data: {

              labels: Object.keys(categories),

              datasets: [

                {

                  label: 'Contracts by Category',

                  data: Object.values(categories)

                }

              ]

            },

            options: {

              responsive: true

            }

          });

        },

        error: (error: any) => {

          console.error(

            'Error loading Contract Categories:',

            error

          );

        }

      });

  }


  // ===============================
  // DEPARTMENT PERFORMANCE CHART
  // ===============================

  createDepartmentPerformanceChart(): void {

    const departments = this.departmentPerformance.map(
      (item: any) => item.department
    );

    const contracts = this.departmentPerformance.map(
      (item: any) => item.contracts
    );

    const obligations = this.departmentPerformance.map(
      (item: any) => item.obligations
    );

    const overdue = this.departmentPerformance.map(
      (item: any) => item.overdue
    );


    new Chart('departmentPerformanceChart', {

      type: 'bar',

      data: {

        labels: departments,

        datasets: [

          {
            label: 'Contracts',
            data: contracts
          },

          {
            label: 'Obligations',
            data: obligations
          },

          {
            label: 'Overdue',
            data: overdue
          }

        ]

      },

      options: {

        responsive: true

      }

    });

  }
// ===============================
// DOWNLOAD FILE HELPER
// ===============================

downloadFile(
  blob: Blob,
  fileName: string
): void {

  const url = window.URL.createObjectURL(blob);

  const link = document.createElement('a');

  link.href = url;

  link.download = fileName;

  link.click();

  window.URL.revokeObjectURL(url);
}


// ===============================
// CONTRACT PDF
// ===============================

downloadContractPdf(): void {

  this.dashboardService
    .downloadContractPdf()
    .subscribe((blob: Blob) => {

      this.downloadFile(
        blob,
        'contract_report.pdf'
      );

    });

}


// ===============================
// CONTRACT EXCEL
// ===============================

downloadContractExcel(): void {

  this.dashboardService
    .downloadContractExcel()
    .subscribe((blob: Blob) => {

      this.downloadFile(
        blob,
        'contract_report.xlsx'
      );

    });

}


// ===============================
// OBLIGATION PDF
// ===============================

downloadObligationPdf(): void {

  this.dashboardService
    .downloadObligationPdf()
    .subscribe((blob: Blob) => {

      this.downloadFile(
        blob,
        'obligation_report.pdf'
      );

    });

}


// ===============================
// OBLIGATION EXCEL
// ===============================

downloadObligationExcel(): void {

  this.dashboardService
    .downloadObligationExcel()
    .subscribe((blob: Blob) => {

      this.downloadFile(
        blob,
        'obligation_report.xlsx'
      );

    });

}


// ===============================
// RENEWAL PDF
// ===============================

downloadRenewalPdf(): void {

  this.dashboardService
    .downloadRenewalPdf()
    .subscribe((blob: Blob) => {

      this.downloadFile(
        blob,
        'renewal_report.pdf'
      );

    });

}


// ===============================
// RENEWAL EXCEL
// ===============================

downloadRenewalExcel(): void {

  this.dashboardService
    .downloadRenewalExcel()
    .subscribe((blob: Blob) => {

      this.downloadFile(
        blob,
        'renewal_report.xlsx'
      );

    });

}


// ===============================
// COMPLIANCE PDF
// ===============================

downloadCompliancePdf(): void {

  this.dashboardService
    .downloadCompliancePdf()
    .subscribe((blob: Blob) => {

      this.downloadFile(
        blob,
        'compliance_report.pdf'
      );

    });

}


// ===============================
// COMPLIANCE EXCEL
// ===============================

downloadComplianceExcel(): void {

  this.dashboardService
    .downloadComplianceExcel()
    .subscribe((blob: Blob) => {

      this.downloadFile(
        blob,
        'compliance_report.xlsx'
      );

    });

}
// ===============================
// LOAD HIGH RISK CONTRACTS
// ===============================

loadHighRiskContracts(): void {

  this.dashboardService
    .getRiskReport()
    .subscribe({

      next: (data: any) => {

        console.log(
          'High Risk Contracts:',
          data
        );

        this.highRiskContracts = data;

        this.cdr.detectChanges();

      },

      error: (error: any) => {

        console.error(
          'Error loading High Risk Contracts:',
          error
        );

      }

    });

}
// ===============================
// LOAD OVERDUE OBLIGATIONS
// ===============================

loadOverdueObligations(): void {

  this.dashboardService
    .getOverdueObligations()
    .subscribe({

      next: (data: any) => {

        console.log(
          'Overdue Obligations:',
          data
        );

        this.overdueObligations = data;

        this.cdr.detectChanges();

      },

      error: (error: any) => {

        console.error(
          'Error loading Overdue Obligations:',
          error
        );

      }

    });

}
}