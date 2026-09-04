import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { Chart } from 'chart.js/auto';

import {
  DashboardService,
  DashboardSummary,
  ContractStats,
  ObligationStats,
  ComplianceStats
} from '../services/dashboard';

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
export class Dashboard implements OnInit {

  summary: DashboardSummary | null = null;
  errorMessage = '';

  contractStats: ContractStats | null = null;
  obligationStats: ObligationStats | null = null;
  complianceStats: ComplianceStats | null = null;

  constructor(
    private dashboardService: DashboardService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {

    this.dashboardService.getDashboardSummary().subscribe({
      next: (data) => {
        this.summary = data;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Dashboard API error:', error);
        this.errorMessage = 'Unable to load dashboard data.';
        this.cdr.markForCheck();
      }
    });

    this.dashboardService.getContractStats().subscribe({
      next: (data) => {
        this.contractStats = data;
        this.cdr.markForCheck();
      },
      error: (error) => console.error('Contract stats error:', error)
    });

    this.dashboardService.getObligationStats().subscribe({
      next: (data) => {
        this.obligationStats = data;
        this.cdr.markForCheck();
      },
      error: (error) => console.error('Obligation stats error:', error)
    });

    this.dashboardService.getComplianceStats().subscribe({
      next: (data) => {
        this.complianceStats = data;
        this.cdr.markForCheck();
      },
      error: (error) => console.error('Compliance stats error:', error)
    });
     setTimeout(() => {
      this.createCharts();
    }, 1000);
  }

  createCharts(): void {

    if (this.contractStats) {
      new Chart('contractChart', {
        type: 'pie',
        data: {
          labels: ['Active', 'Draft', 'Under Review', 'Approved', 'Expired'],
          datasets: [{
            data: [
              this.contractStats.active,
              this.contractStats.draft,
              this.contractStats.under_review,
              this.contractStats.approved,
              this.contractStats.expired
            ]
          }]
        }
      });

      const categories = Object.keys(this.contractStats.by_category);
      const categoryValues = Object.values(this.contractStats.by_category);

      new Chart('categoryChart', {
        type: 'bar',
        data: {
          labels: categories,
          datasets: [{
            label: 'Contracts',
            data: categoryValues
          }]
        }
      });
    }

    if (this.obligationStats) {
      new Chart('obligationChart', {
        type: 'doughnut',
        data: {
          labels: ['Pending', 'In Progress', 'Completed', 'Delayed', 'Overdue'],
          datasets: [{
            data: [
              this.obligationStats.pending,
              this.obligationStats.in_progress,
              this.obligationStats.completed,
              this.obligationStats.delayed,
              this.obligationStats.overdue
            ]
          }]
        }
      });
    }

    if (this.complianceStats) {
      new Chart('complianceChart', {
        type: 'bar',
        data: {
          labels: ['Compliant', 'Pending', 'Delayed', 'Non-Compliant', 'High Risk'],
          datasets: [{
            label: 'Contracts',
            data: [
              this.complianceStats.compliant,
              this.complianceStats.pending,
              this.complianceStats.delayed,
              this.complianceStats.non_compliant,
              this.complianceStats.high_risk
            ]
          }]
        }
      });
    }
  }
}