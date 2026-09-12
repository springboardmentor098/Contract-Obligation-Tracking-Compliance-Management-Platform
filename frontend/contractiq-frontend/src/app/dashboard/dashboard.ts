import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  OnDestroy
} from '@angular/core';

import { CommonModule } from '@angular/common';

import {
  MatCardModule
} from '@angular/material/card';

import {
  MatButtonModule
} from '@angular/material/button';

import {
  Router
} from '@angular/router';

import { Auth } from '../services/auth';

import {
  Dashboard as DashboardService,
  DashboardData,
  ContractReport
} from '../services/dashboard';

import {
  Chart,
  ArcElement,
  BarElement,
  BarController,
  DoughnutController,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from 'chart.js';


// =====================================================
// REGISTER CHART.JS COMPONENTS
// =====================================================

Chart.register(
  ArcElement,
  BarElement,
  BarController,
  DoughnutController,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);


// =====================================================
// COMPONENT
// =====================================================

@Component({
  selector: 'app-dashboard',

  standalone: true,

  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule
  ],

  templateUrl: './dashboard.html',

  styleUrl: './dashboard.less'
})
export class Dashboard
  implements AfterViewInit, OnDestroy {


  // ===================================================
  // DASHBOARD DATA
  // ===================================================

  dashboardData: DashboardData | null = null;


  // ===================================================
  // CONTRACT REPORT
  // ===================================================

  contractReport: ContractReport | null = null;


  // ===================================================
  // DASHBOARD CARD VALUES
  // ===================================================

  totalContracts = 0;

  activeContracts = 0;

  pendingObligations = 0;

  overdueObligations = 0;

  upcomingRenewals = 0;

  highRiskContracts = 0;


  // ===================================================
  // UI STATE
  // ===================================================

  loading = false;

  refreshing = false;

  isEmpty = false;

  errorMessage = '';


  // ===================================================
  // CHART REFERENCES
  // ===================================================

  private contractStatusChart: Chart | null = null;

  private obligationStatusChart: Chart | null = null;

  private complianceChart: Chart | null = null;

  private categoryChart: Chart | null = null;


  // ===================================================
  // CONSTRUCTOR
  // ===================================================

  constructor(
    private dashboardService: DashboardService,

    private cdr: ChangeDetectorRef,

    private auth: Auth,

    private router: Router
  ) {}


  // ===================================================
  // COMPONENT INITIALIZATION
  // ===================================================

  ngAfterViewInit(): void {

    this.loadDashboardData();

  }


  // ===================================================
  // LOAD DASHBOARD DATA
  // ===================================================

  loadDashboardData(): void {

    this.loading = true;

    this.refreshing = true;

    this.errorMessage = '';

    this.isEmpty = false;


    // ---------------------------------------------------
    // Destroy old charts before creating new ones
    // ---------------------------------------------------

    this.destroyCharts();


    // ---------------------------------------------------
    // Reset old data
    // ---------------------------------------------------

    this.dashboardData = null;

    this.contractReport = null;


    this.totalContracts = 0;

    this.activeContracts = 0;

    this.pendingObligations = 0;

    this.overdueObligations = 0;

    this.upcomingRenewals = 0;

    this.highRiskContracts = 0;


    this.cdr.detectChanges();


    // ===================================================
    // DASHBOARD API
    // ===================================================

    this.dashboardService
      .getDashboardSummary()
      .subscribe({

        next: (data: DashboardData) => {

          console.log(
            'Dashboard API data:',
            data
          );


          // ------------------------------------------------
          // Store dashboard response
          // ------------------------------------------------

          this.dashboardData = data;


          // ------------------------------------------------
          // Update KPI values
          // ------------------------------------------------

          this.totalContracts =
            data.contracts.total;


          this.activeContracts =
            data.contracts.active;


          this.pendingObligations =
            data.obligations.pending;


          this.overdueObligations =
            data.obligations.overdue;


          this.upcomingRenewals =
            data.renewals.upcoming;


          this.highRiskContracts =
            data.compliance.high_risk;


          // ------------------------------------------------
          // Empty state
          // ------------------------------------------------

          this.isEmpty =
            data.contracts.total === 0 &&
            data.obligations.total === 0 &&
            data.renewals.upcoming === 0 &&
            data.compliance.total === 0;


          // ------------------------------------------------
          // Stop loading
          // ------------------------------------------------

          this.loading = false;

          this.refreshing = false;


          this.cdr.detectChanges();


          // ------------------------------------------------
          // Wait for canvas elements to render
          // ------------------------------------------------

          setTimeout(() => {

            if (!this.dashboardData) {
              return;
            }


            this.createContractStatusChart();

            this.createObligationStatusChart();

            this.createComplianceChart();


            this.cdr.detectChanges();


            // ----------------------------------------------
            // Load contract category report
            // ----------------------------------------------

            this.loadContractCategories();

          });

        },


        // =================================================
        // ERROR
        // =================================================

        error: (error: any) => {

          console.error(
            'Dashboard API error:',
            error
          );


          this.loading = false;

          this.refreshing = false;

          this.isEmpty = false;


          // ------------------------------------------------
          // Error messages
          // ------------------------------------------------

          if (error?.status === 401) {

            this.errorMessage =
              'Your session has expired. Please login again.';

          }

          else if (error?.status === 403) {

            this.errorMessage =
              'You are not authorized to view dashboard data.';

          }

          else if (error?.status === 0) {

            this.errorMessage =
              'Unable to connect to the backend server.';

          }

          else {

            this.errorMessage =
              'Unable to load dashboard data. Please try again.';

          }


          this.cdr.detectChanges();

        }

      });

  }


  // =====================================================
  // LOAD CONTRACT CATEGORY DATA
  // =====================================================

  loadContractCategories(): void {

    this.dashboardService
      .getContractSummary()
      .subscribe({

        next: (data: ContractReport) => {

          console.log(
            'Contract Report data:',
            data
          );


          this.contractReport = data;


          // ------------------------------------------------
          // Create category chart
          // ------------------------------------------------

          setTimeout(() => {

            this.createCategoryChart(
              data.contracts_by_category
            );

            this.cdr.detectChanges();

          });

        },


        error: (error: any) => {

          console.error(
            'Contract Categories API error:',
            error
          );

          // -----------------------------------------------
          // Do not break complete dashboard if this
          // secondary API fails.
          // -----------------------------------------------

          this.contractReport = null;

          this.cdr.detectChanges();

        }

      });

  }


  // =====================================================
  // NAVIGATION
  // =====================================================

  goToContracts(): void {

    this.router.navigate([
      '/contracts'
    ]);

  }


  goToObligations(): void {

    this.router.navigate([
      '/obligations'
    ]);

  }


  goToRenewals(): void {

    this.router.navigate([
      '/renewals'
    ]);

  }


  goToCompliance(): void {

    this.router.navigate([
      '/compliance'
    ]);

  }


  goToReports(): void {

    this.router.navigate([
      '/reports'
    ]);

  }


  // =====================================================
  // LOGOUT
  // =====================================================

  logout(): void {

    this.auth.logout();

    this.router.navigate([
      '/login'
    ]);

  }


  // =====================================================
  // CONTRACT STATUS CHART
  // =====================================================

  createContractStatusChart(): void {

    if (!this.dashboardData) {
      return;
    }


    const canvas =
      document.getElementById(
        'contractStatusChart'
      ) as HTMLCanvasElement | null;


    if (!canvas) {

      console.warn(
        'Contract status canvas not found.'
      );

      return;

    }


    // ---------------------------------------------------
    // Destroy existing chart
    // ---------------------------------------------------

    this.contractStatusChart?.destroy();


    this.contractStatusChart =
      new Chart(
        canvas,
        {

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

                  this.dashboardData
                    .contracts
                    .draft,

                  this.dashboardData
                    .contracts
                    .under_review,

                  this.dashboardData
                    .contracts
                    .approved,

                  this.dashboardData
                    .contracts
                    .active,

                  this.dashboardData
                    .contracts
                    .expired,

                  this.dashboardData
                    .contracts
                    .terminated

                ],

                backgroundColor: [

                  '#94a3b8',

                  '#f59e0b',

                  '#16a34a',

                  '#2563eb',

                  '#dc2626',

                  '#7f1d1d'

                ],

                borderRadius: 8,

                borderSkipped: false

              }

            ]

          },

          options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

              legend: {

                display: false

              },

              tooltip: {

                backgroundColor:
                  '#0f172a',

                padding: 12,

                cornerRadius: 8

              }

            },

            scales: {

              x: {

                grid: {

                  display: false

                }

              },

              y: {

                beginAtZero: true,

                ticks: {

                  precision: 0

                }

              }

            }

          }

        }

      );

  }


  // =====================================================
  // OBLIGATION STATUS CHART
  // =====================================================

  createObligationStatusChart(): void {

    if (!this.dashboardData) {
      return;
    }


    const canvas =
      document.getElementById(
        'obligationStatusChart'
      ) as HTMLCanvasElement | null;


    if (!canvas) {

      console.warn(
        'Obligation status canvas not found.'
      );

      return;

    }


    this.obligationStatusChart?.destroy();


    this.obligationStatusChart =
      new Chart(
        canvas,
        {

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

                  this.dashboardData
                    .obligations
                    .pending,

                  this.dashboardData
                    .obligations
                    .in_progress,

                  this.dashboardData
                    .obligations
                    .completed,

                  this.dashboardData
                    .obligations
                    .delayed,

                  this.dashboardData
                    .obligations
                    .overdue

                ],

                backgroundColor: [

                  '#f59e0b',

                  '#2563eb',

                  '#16a34a',

                  '#ea580c',

                  '#dc2626'

                ],

                borderRadius: 8,

                borderSkipped: false

              }

            ]

          },

          options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

              legend: {

                display: false

              },

              tooltip: {

                backgroundColor:
                  '#0f172a',

                padding: 12,

                cornerRadius: 8

              }

            },

            scales: {

              x: {

                grid: {

                  display: false

                }

              },

              y: {

                beginAtZero: true,

                ticks: {

                  precision: 0

                }

              }

            }

          }

        }

      );

  }


  // =====================================================
  // COMPLIANCE CHART
  // =====================================================

  createComplianceChart(): void {

    if (!this.dashboardData) {
      return;
    }


    const canvas =
      document.getElementById(
        'complianceChart'
      ) as HTMLCanvasElement | null;


    if (!canvas) {

      console.warn(
        'Compliance canvas not found.'
      );

      return;

    }


    this.complianceChart?.destroy();


    this.complianceChart =
      new Chart(
        canvas,
        {

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

                data: [

                  this.dashboardData
                    .compliance
                    .compliant,

                  this.dashboardData
                    .compliance
                    .pending,

                  this.dashboardData
                    .compliance
                    .delayed,

                  this.dashboardData
                    .compliance
                    .non_compliant,

                  this.dashboardData
                    .compliance
                    .high_risk

                ],

                backgroundColor: [

                  '#16a34a',

                  '#f59e0b',

                  '#ea580c',

                  '#dc2626',

                  '#7c3aed'

                ],

                borderWidth: 4,

                borderColor: '#ffffff'

              }

            ]

          },

          options: {

            responsive: true,

            maintainAspectRatio: false,

            cutout: '68%',

            plugins: {

              legend: {

                position: 'bottom',

                labels: {

                  usePointStyle: true,

                  padding: 16

                }

              },

              tooltip: {

                backgroundColor:
                  '#0f172a',

                padding: 12,

                cornerRadius: 8

              }

            }

          }

        }

      );

  }


  // =====================================================
  // CONTRACT CATEGORY CHART
  // =====================================================

  createCategoryChart(
    categories: {
      [key: string]: number
    }
  ): void {

    if (!categories) {
      return;
    }


    const canvas =
      document.getElementById(
        'categoryChart'
      ) as HTMLCanvasElement | null;


    if (!canvas) {

      console.warn(
        'Category canvas not found.'
      );

      return;

    }


    this.categoryChart?.destroy();


    const labels =
      Object.keys(categories);


    const values =
      Object.values(categories);


    this.categoryChart =
      new Chart(
        canvas,
        {

          type: 'bar',

          data: {

            labels,

            datasets: [

              {

                label: 'Contracts',

                data: values,

                backgroundColor: [

                  '#2563eb',

                  '#7c3aed',

                  '#16a34a',

                  '#f59e0b',

                  '#ea580c',

                  '#dc2626'

                ],

                borderRadius: 8,

                borderSkipped: false

              }

            ]

          },

          options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

              legend: {

                display: false

              },

              tooltip: {

                backgroundColor:
                  '#0f172a',

                padding: 12,

                cornerRadius: 8

              }

            },

            scales: {

              x: {

                grid: {

                  display: false

                }

              },

              y: {

                beginAtZero: true,

                ticks: {

                  precision: 0

                }

              }

            }

          }

        }

      );

  }


  // =====================================================
  // DESTROY ALL CHARTS
  // =====================================================

  private destroyCharts(): void {

    this.contractStatusChart?.destroy();

    this.obligationStatusChart?.destroy();

    this.complianceChart?.destroy();

    this.categoryChart?.destroy();


    this.contractStatusChart = null;

    this.obligationStatusChart = null;

    this.complianceChart = null;

    this.categoryChart = null;

  }


  // =====================================================
  // COMPONENT DESTROY
  // =====================================================

  ngOnDestroy(): void {

    this.destroyCharts();

  }

}