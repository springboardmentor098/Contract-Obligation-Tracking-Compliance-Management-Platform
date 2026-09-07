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
  imports: [
    CommonModule,
    MatCardModule
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit, AfterViewInit {

  activeContracts = 0;
  upcomingRenewals = 0;
  pendingObligations = 0;
  complianceStatus = 0;

  loading = true;
  errorMessage = '';

  private dashboardData: any = null;

  constructor(
    private dashboardService: DashboardService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  ngAfterViewInit(): void {

    // Charts will be created after API data arrives.
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

          console.log(
            'Dashboard API response:',
            data
          );

          this.dashboardData = data;

          // ==============================
          // SUMMARY CARDS
          // ==============================

          this.activeContracts =
            data.contracts?.active ?? 0;

          this.upcomingRenewals =
            data.renewals?.upcoming ?? 0;

          this.pendingObligations =
            data.obligations?.pending ?? 0;

          this.complianceStatus =
            data.compliance?.average_score ?? 0;

          this.loading = false;

          this.cdr.detectChanges();

          // Create charts after Angular renders canvas elements.
          setTimeout(() => {
            this.createCharts();
          }, 100);

        },

        error: (error) => {

          console.error(
            'Dashboard API error:',
            error
          );

          this.errorMessage =
            'Unable to load dashboard data.';

          this.loading = false;

          this.cdr.detectChanges();
        }

      });
  }

  createCharts(): void {

    if (!this.dashboardData) {
      return;
    }

    this.createContractCategoryChart();

    this.createObligationStatusChart();

    this.createRenewalStatusChart();

    this.createComplianceStatusChart();
  }

  // =====================================================
  // CONTRACT CATEGORY CHART
  // =====================================================

  createContractCategoryChart(): void {

    const canvas =
      document.getElementById(
        'contractCategoryChart'
      ) as HTMLCanvasElement;

    if (!canvas) {
      return;
    }

    const categories =
      this.dashboardData.contracts.by_category;

    const labels =
      Object.keys(categories);

    const values =
      Object.values(categories) as number[];

    new Chart(canvas, {

      type: 'bar',

      data: {

        labels: labels,

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

  // =====================================================
  // OBLIGATION STATUS CHART
  // =====================================================

  createObligationStatusChart(): void {

    const canvas =
      document.getElementById(
        'obligationStatusChart'
      ) as HTMLCanvasElement;

    if (!canvas) {
      return;
    }

    const obligations =
      this.dashboardData.obligations;

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
              obligations.pending,
              obligations.in_progress,
              obligations.completed,
              obligations.delayed,
              obligations.overdue
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

  // =====================================================
  // RENEWAL STATUS CHART
  // =====================================================

  createRenewalStatusChart(): void {

    const canvas =
      document.getElementById(
        'renewalStatusChart'
      ) as HTMLCanvasElement;

    if (!canvas) {
      return;
    }

    const renewals =
      this.dashboardData.renewals;

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
              renewals.upcoming,
              renewals.in_progress,
              renewals.renewed,
              renewals.expired,
              renewals.cancelled
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

  // =====================================================
  // COMPLIANCE STATUS CHART
  // =====================================================

  createComplianceStatusChart(): void {

    const canvas =
      document.getElementById(
        'complianceStatusChart'
      ) as HTMLCanvasElement;

    if (!canvas) {
      return;
    }

    const compliance =
      this.dashboardData.compliance;

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
              compliance.compliant,
              compliance.pending,
              compliance.delayed,
              compliance.non_compliant,
              compliance.high_risk
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