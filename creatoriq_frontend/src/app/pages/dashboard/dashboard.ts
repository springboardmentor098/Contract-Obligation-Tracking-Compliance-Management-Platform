import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  OnDestroy,
  OnInit
} from '@angular/core';

import {
  Dashboard as DashboardService,
  DashboardSummary,
  ContractSummary,
  ObligationSummary,
  RenewalSummary,
  ComplianceSummary
} from '../../services/dashboard';

import {
  Chart,
  ChartConfiguration,
  registerables
} from 'chart.js';

import { forkJoin } from 'rxjs';

Chart.register(...registerables);

/*
 * Chart.js light-theme defaults.
 * The dashboard uses a white/light background, so chart labels,
 * axes and grid lines need explicit readable colors.
 */
Chart.defaults.color = '#374151';
Chart.defaults.borderColor = '#e5e7eb';
Chart.defaults.font.family = 'Arial, Helvetica, sans-serif';


@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard
  implements OnInit, AfterViewInit, OnDestroy {

  summary: DashboardSummary | null = null;

  contractSummary: ContractSummary | null = null;

  obligationSummary: ObligationSummary | null = null;

  renewalSummary: RenewalSummary | null = null;

  complianceSummary: ComplianceSummary | null = null;

  loading = true;

  errorMessage = '';

  private charts: Chart[] = [];

  private viewReady = false;

  constructor(
    private dashboardService: DashboardService,
    private changeDetectorRef: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  ngAfterViewInit(): void {
    this.viewReady = true;

    requestAnimationFrame(() => {
      this.createChartsIfReady();
    });
  }

  ngOnDestroy(): void {
    this.destroyCharts();
  }

  loadDashboard(): void {

    this.loading = true;

    this.errorMessage = '';

    console.log('Loading dashboard data...');

    forkJoin({

      summary:
        this.dashboardService.getDashboardSummary(),

      contracts:
        this.dashboardService.getContractSummary(),

      obligations:
        this.dashboardService.getObligationSummary(),

      renewals:
        this.dashboardService.getRenewalSummary(),

      compliance:
        this.dashboardService.getComplianceSummary()

    }).subscribe({

      next: (data) => {

        console.log(
          'All dashboard data received:',
          data
        );

        this.summary = data.summary;

        this.contractSummary = data.contracts;

        this.obligationSummary = data.obligations;

        this.renewalSummary = data.renewals;

        this.complianceSummary = data.compliance;

        this.loading = false;

        console.log(
          'Dashboard loading:',
          this.loading
        );

        /*
         * Force Angular to update the template
         * after the asynchronous API response.
         */
        this.changeDetectorRef.detectChanges();

        /*
         * Wait until Angular has rendered the
         * canvas elements before creating charts.
         */
        setTimeout(() => {

          requestAnimationFrame(() => {
            this.createChartsIfReady();
          });

        }, 0);

      },

      error: (error) => {

        console.error(
          'Dashboard API error:',
          error
        );

        this.loading = false;

        if (error.status === 401) {

          this.errorMessage =
            'Your session has expired. Please log in again.';

        } else if (error.status === 403) {

          this.errorMessage =
            'You do not have permission to view this dashboard.';

        } else {

          this.errorMessage =
            'Unable to load dashboard data.';

        }

        this.changeDetectorRef.detectChanges();

      }

    });
  }

  private createChartsIfReady(): void {

    if (
      !this.viewReady ||
      !this.summary ||
      !this.contractSummary ||
      !this.obligationSummary ||
      !this.complianceSummary
    ) {

      return;
    }

    this.destroyCharts();

    this.createContractStatusChart();

    this.createObligationStatusChart();

    this.createComplianceChart();

    this.createContractCategoryChart();
  }

  private createContractStatusChart(): void {

    const canvas =
      document.getElementById(
        'contractStatusChart'
      ) as HTMLCanvasElement | null;

    if (
      !canvas ||
      !canvas.getContext('2d') ||
      !this.summary
    ) {

      return;
    }

    /*
     * Contract Status Chart
     *
     * Required statuses:
     * Draft
     * Under Review
     * Approved
     * Active
     * Expired
     * Terminated
     *
     * The order here matches the Sprint 13
     * dashboard requirement.
     */

    const config:
      ChartConfiguration<'doughnut'> = {

      type: 'doughnut',

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

            data: [

              this.summary.contracts.draft,

              this.summary.contracts.under_review,

              this.summary.contracts.approved,

              this.summary.contracts.active,

              this.summary.contracts.expired,

              this.summary.contracts.terminated

            ],

            backgroundColor: [
              '#94a3b8',
              '#f59e0b',
              '#8b5cf6',
              '#10b981',
              '#ef4444',
              '#f43f5e'
            ],

            borderColor: '#ffffff',
            borderWidth: 2
          }

        ]

      },

      options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

          legend: {

            position: 'bottom',

            labels: {
              color: '#374151',
              padding: 16
            }

          }

        }

      }

    };

    this.charts.push(
      new Chart(
        canvas,
        config
      )
    );
  }

  private createObligationStatusChart(): void {

    const canvas =
      document.getElementById(
        'obligationStatusChart'
      ) as HTMLCanvasElement | null;

    if (
      !canvas ||
      !canvas.getContext('2d') ||
      !this.obligationSummary
    ) {

      return;
    }

    const config:
      ChartConfiguration<'bar'> = {

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

              this.obligationSummary.pending,

              this.obligationSummary.in_progress,

              this.obligationSummary.completed,

              this.obligationSummary.delayed,

              this.obligationSummary.overdue

            ],

            backgroundColor: [
              '#f59e0b',
              '#3b82f6',
              '#10b981',
              '#f97316',
              '#ef4444'
            ],

            borderColor: '#ffffff',
            borderWidth: 1
          }

        ]

      },

      options: {

        responsive: true,

        maintainAspectRatio: false,

        scales: {

          y: {

            beginAtZero: true,

            ticks: {
              precision: 0,
              color: '#4b5563'
            },

            grid: {
              color: '#e5e7eb'
            }

          }

        },

        plugins: {

          legend: {

            display: false

          }

        }

      }

    };

    this.charts.push(
      new Chart(
        canvas,
        config
      )
    );
  }

  private createComplianceChart(): void {

    const canvas =
      document.getElementById(
        'complianceChart'
      ) as HTMLCanvasElement | null;

    if (
      !canvas ||
      !canvas.getContext('2d') ||
      !this.complianceSummary
    ) {

      return;
    }

    const config:
      ChartConfiguration<'doughnut'> = {

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

              this.complianceSummary.compliant,

              this.complianceSummary.pending,

              this.complianceSummary.delayed,

              this.complianceSummary.non_compliant,

              this.complianceSummary.high_risk

            ],

            backgroundColor: [
              '#10b981',
              '#f59e0b',
              '#f97316',
              '#ef4444',
              '#b91c1c'
            ],

            borderColor: '#ffffff',
            borderWidth: 2
          }

        ]

      },

      options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

          legend: {

            position: 'bottom',

            labels: {
              color: '#374151',
              padding: 16
            }

          }

        }

      }

    };

    this.charts.push(
      new Chart(
        canvas,
        config
      )
    );
  }

  private createContractCategoryChart(): void {

    const canvas =
      document.getElementById(
        'contractCategoryChart'
      ) as HTMLCanvasElement | null;

    if (
      !canvas ||
      !canvas.getContext('2d') ||
      !this.contractSummary
    ) {

      return;
    }

    /*
     * Backend returns:
     *
     * "contracts_by_category": {
     *   "Compliance": 5,
     *   "Consulting": 5,
     *   "Technology": 5
     * }
     *
     * Therefore we must use contracts_by_category
     * instead of by_category.
     */

    const categories =
      Object.keys(
        this.contractSummary.contracts_by_category || {}
      );

    const values =
      categories.map(
        (category) =>
          this.contractSummary!
            .contracts_by_category[category]
      );

    const config:
      ChartConfiguration<'bar'> = {

      type: 'bar',

      data: {

        labels: categories,

        datasets: [

          {

            label: 'Contracts',

            data: values,

            backgroundColor: [
              '#3b82f6',
              '#8b5cf6',
              '#10b981',
              '#f59e0b',
              '#ef4444',
              '#06b6d4',
              '#6366f1'
            ],

            borderColor: '#ffffff',
            borderWidth: 1
          }

        ]

      },

      options: {

        responsive: true,

        maintainAspectRatio: false,

        indexAxis: 'y',

        scales: {

          x: {

            beginAtZero: true,

            ticks: {
              precision: 0,
              color: '#4b5563'
            },

            grid: {
              color: '#e5e7eb'
            }

          },

          y: {
            ticks: {
              color: '#4b5563'
            },

            grid: {
              color: '#f1f5f9'
            }
          }

        },

        plugins: {

          legend: {

            display: false

          }

        }

      }

    };

    this.charts.push(
      new Chart(
        canvas,
        config
      )
    );
  }

  private destroyCharts(): void {

    this.charts.forEach(
      (chart) => chart.destroy()
    );

    this.charts = [];
  }

  getCompliancePercentage(
    value: number
  ): number {

    if (!this.summary) {

      return 0;
    }

    const total =
      this.summary.compliance.compliant +

      this.summary.compliance.pending +

      this.summary.compliance.delayed +

      this.summary.compliance.non_compliant +

      this.summary.compliance.high_risk;

    if (total === 0) {

      return 0;
    }

    return (
      value / total
    ) * 100;
  }

}