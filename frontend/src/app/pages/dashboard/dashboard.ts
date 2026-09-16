import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  DashboardService,
  DashboardSummary
} from '../../core/services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit {
  private readonly dashboardService = inject(DashboardService);

  summary = signal<DashboardSummary | null>(null);
  loading = signal(true);
  error = signal('');

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading.set(true);
    this.error.set('');

    this.dashboardService.getDashboardSummary().subscribe({
      next: (data) => {
        console.log('Dashboard data received:', data);

        this.summary.set(data);
        this.loading.set(false);

        console.log('Dashboard summary signal:', this.summary());
        console.log('Dashboard loading signal:', this.loading());
        console.log('Dashboard error signal:', this.error());
      },

      error: (err) => {
        console.error('Dashboard API error:', err);

        this.error.set(
          'Dashboard API error: ' +
          (err?.status ?? 'unknown') +
          ' - ' +
          (err?.message ?? 'Unknown error')
        );

        this.loading.set(false);
      }
    });
  }
}
