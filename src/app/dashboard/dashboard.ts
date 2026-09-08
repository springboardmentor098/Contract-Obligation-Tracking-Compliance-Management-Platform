import {
  Component,
  OnInit,
  ChangeDetectorRef,
  AfterViewInit
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';

import { Chart } from 'chart.js/auto';

import { DashboardService } from '../services/dashboard';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit, AfterViewInit {

  totalContracts = 0;
  activeContracts = 0;
  expiredContracts = 0;

  pendingObligations = 0;
  overdueObligations = 0;

  upcomingRenewals = 0;

  complianceStatus = 0;

  loading = true;
  errorMessage = '';

  private dashboardData: any = null;

  private chartsCreated = false;

  constructor(
    private dashboardService: DashboardService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  ngAfterViewInit(): void {
    if (this.dashboardData) {
      this.createCharts();
    }
  }

  loadDashboardData(): void {

    this.loading = true;
    this.errorMessage = '';

    this.dashboardService
      .getDashboardSummary()
      .subscribe({

        next: (data) => {

          console.log('Dashboard API response:', data);

          this.dashboardData = data;

          this.totalContracts =
            data.contracts?.total ?? 0;

          this.activeContracts =
            data.contracts?.active ?? 0;

          this.expiredContracts =
            data.contracts?.expired ?? 0;

          this.pendingObligations =
            data.obligations?.pending ?? 0;

          this.overdueObligations =
            data.obligations?.overdue ?? 0;

          this.upcomingRenewals =
            data.renewals?.upcoming ?? 0;

          this.complianceStatus =
            data.compliance?.average_score ?? 0;

          this.loading = false;

          this.cdr.detectChanges();

          setTimeout(() => {
            this.createCharts();
          }, 100);
        },

        error: (error) => {

          console.error('Dashboard API error:', error);

          this.loading = false;

          this.errorMessage =
            'Unable to load dashboard data. Please try again.';

          this.cdr.detectChanges();
        }

      });
  }

  createCharts(): void {

    if (!this.dashboardData || this.chartsCreated) {
      return;
    }

    this.createContractCategoryChart();
    this.createObligationStatusChart();
    this.createRenewalStatusChart();
    this.createComplianceStatusChart();

    this.chartsCreated = true;
  }

  createContractCategoryChart(): void {

    const canvas =
      document.getElementById(
        'contractCategoryChart'
      ) as HTMLCanvasElement;

    if (!canvas) {
      return;
    }

    const categories =
      this.dashboardData.contracts?.by_category ?? {};

    const labels = Object.keys(categories);
    const values = Object.values(categories) as number[];

    new Chart(canvas, {
      type: 'bar',

      data: {
        labels,

        datasets: [
          {
            label: 'Contracts',
            data: values
          }
        ]
      },

      options: {
        responsive: true,
        maintainAspectRatio: false,

        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }

  createObligationStatusChart(): void {

    const canvas =
      document.getElementById(
        'obligationStatusChart'
      ) as HTMLCanvasElement;

    if (!canvas) {
      return;
    }

    const obligations =
      this.dashboardData.obligations ?? {};

    new Chart(canvas, {
      type: 'doughnut',

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
            data: [
              obligations.pending ?? 0,
              obligations.in_progress ?? 0,
              obligations.completed ?? 0,
              obligations.delayed ?? 0,
              obligations.overdue ?? 0
            ]
          }
        ]
      },

      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }

  createRenewalStatusChart(): void {

    const canvas =
      document.getElementById(
        'renewalStatusChart'
      ) as HTMLCanvasElement;

    if (!canvas) {
      return;
    }

    const renewals =
      this.dashboardData.renewals ?? {};

    new Chart(canvas, {
      type: 'pie',

      data: {

        labels: [
          'Upcoming',
          'In Progress',
          'Renewed',
          'Expired',
          'Cancelled'
        ],

        datasets: [
          {
            data: [
              renewals.upcoming ?? 0,
              renewals.in_progress ?? 0,
              renewals.renewed ?? 0,
              renewals.expired ?? 0,
              renewals.cancelled ?? 0
            ]
          }
        ]
      },

      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }

  createComplianceStatusChart(): void {

    const canvas =
      document.getElementById(
        'complianceStatusChart'
      ) as HTMLCanvasElement;

    if (!canvas) {
      return;
    }

    const compliance =
      this.dashboardData.compliance ?? {};

    new Chart(canvas, {
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
              compliance.compliant ?? 0,
              compliance.pending ?? 0,
              compliance.delayed ?? 0,
              compliance.non_compliant ?? 0,
              compliance.high_risk ?? 0
            ]
          }
        ]
      },

      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
}