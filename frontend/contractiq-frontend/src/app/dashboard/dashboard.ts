import {
  AfterViewInit,
  Component,
  ChangeDetectorRef
} from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

import { Auth } from '../services/auth';

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

interface DashboardData {
  contracts: {
    total: number;
    active: number;
    draft: number;
    under_review: number;
    approved: number;
    expired: number;
    terminated: number;
  };

  obligations: {
    total: number;
    pending: number;
    in_progress: number;
    completed: number;
    delayed: number;
    overdue: number;
  };

  renewals: {
    upcoming: number;
    in_progress: number;
    renewed: number;
    expired: number;
    cancelled: number;
  };

  compliance: {
    total: number;
    compliant: number;
    pending: number;
    delayed: number;
    non_compliant: number;
    high_risk: number;
    average_score: number;
  };
}

interface ContractReport {
  total_contracts: number;
  active_contracts: number;
  expired_contracts: number;
  pending_approval_contracts: number;

  contracts_by_status: {
    [key: string]: number;
  };

  contracts_by_category: {
    [key: string]: number;
  };
}

@Component({
  selector: 'app-dashboard',
  standalone: true,

  imports: [
    MatCardModule,
    MatButtonModule
  ],

  templateUrl: './dashboard.html',
  styleUrl: './dashboard.less'
})
export class Dashboard implements AfterViewInit {

  private apiUrl = 'http://127.0.0.1:8000';

  dashboardData!: DashboardData;

  // Dashboard card values
  totalContracts = 0;
  activeContracts = 0;
  pendingObligations = 0;
  overdueObligations = 0;
  upcomingRenewals = 0;
  highRiskContracts = 0;

  constructor(
    private http: HttpClient,
    private cdr: ChangeDetectorRef,
    private auth: Auth,
    private router: Router
  ) {}

  ngAfterViewInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {

    this.http.get<DashboardData>(
      `${this.apiUrl}/dashboard/summary`
    ).subscribe({

      next: (data) => {

        console.log('Dashboard API data:', data);

        this.dashboardData = data;

        // Dashboard card values
        this.totalContracts = data.contracts.total;
        this.activeContracts = data.contracts.active;
        this.pendingObligations = data.obligations.pending;
        this.overdueObligations = data.obligations.overdue;
        this.upcomingRenewals = data.renewals.upcoming;
        this.highRiskContracts = data.compliance.high_risk;

        // Update UI
        this.cdr.detectChanges();

        // Create charts
        this.createContractStatusChart();
        this.createObligationStatusChart();
        this.createComplianceChart();

        // Load contract category data
        this.loadContractCategories();
      },

      error: (error) => {
        console.error('Dashboard API error:', error);
      }

    });
  }

  loadContractCategories(): void {

    this.http.get<ContractReport>(
      `${this.apiUrl}/reports/contracts/summary`
    ).subscribe({

      next: (data) => {

        console.log('Contract Report data:', data);

        this.createCategoryChart(
          data.contracts_by_category
        );
      },

      error: (error) => {

        console.error(
          'Contract Categories API error:',
          error
        );

      }

    });
  }

  logout(): void {

    this.auth.logout();

    this.router.navigate(['/login']);
  }

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
            ],

            backgroundColor: [
              '#94a3b8',
              '#f59e0b',
              '#16a34a',
              '#2563eb',
              '#dc2626',
              '#7f1d1d'
            ],

            borderRadius: 6
          }
        ]

      },

      options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

          legend: {
            display: true
          }

        },

        scales: {

          y: {

            beginAtZero: true,

            ticks: {
              precision: 0
            }

          }

        }

      }

    });
  }

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
            ],

            backgroundColor: [
              '#f59e0b',
              '#2563eb',
              '#16a34a',
              '#ea580c',
              '#dc2626'
            ],

            borderRadius: 6
          }
        ]

      },

      options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

          legend: {
            display: true
          }

        },

        scales: {

          y: {

            beginAtZero: true,

            ticks: {
              precision: 0
            }

          }

        }

      }

    });
  }

  createComplianceChart(): void {

    new Chart('complianceChart', {

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
              this.dashboardData.compliance.compliant,
              this.dashboardData.compliance.pending,
              this.dashboardData.compliance.delayed,
              this.dashboardData.compliance.non_compliant,
              this.dashboardData.compliance.high_risk
            ],

            backgroundColor: [
              '#16a34a',
              '#f59e0b',
              '#ea580c',
              '#dc2626',
              '#7c3aed'
            ],

            borderWidth: 3,

            borderColor: '#ffffff'
          }
        ]

      },

      options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

          legend: {
            position: 'top'
          }

        }

      }

    });
  }

  createCategoryChart(
    categories: { [key: string]: number }
  ): void {

    new Chart('categoryChart', {

      type: 'bar',

      data: {

        labels: Object.keys(categories),

        datasets: [
          {
            label: 'Contracts by Category',

            data: Object.values(categories),

            backgroundColor: [
              '#2563eb',
              '#7c3aed',
              '#16a34a',
              '#f59e0b',
              '#ea580c',
              '#dc2626'
            ],

            borderRadius: 6
          }
        ]

      },

      options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

          legend: {
            display: true
          }

        },

        scales: {

          y: {

            beginAtZero: true,

            ticks: {
              precision: 0
            }

          }

        }

      }

    });
  }

}