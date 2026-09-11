import { Component, ChangeDetectorRef, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api } from '../../services/api';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit {
  private api = inject(Api);
  private cdr = inject(ChangeDetectorRef);

  loading = true;
  error = '';
  data: any = null;

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    this.error = '';
    this.cdr.detectChanges();

    console.log('Dashboard: starting API request');

    this.api.getDashboardSummary().subscribe({
      next: (response) => {
        console.log('Dashboard API response:', response);

        this.data = response;
        this.loading = false;

        this.cdr.detectChanges();

        console.log('Dashboard: loading =', this.loading);
        console.log('Dashboard: data =', this.data);
      },
      error: (err) => {
        console.error('Dashboard API error:', err);

        this.loading = false;

        if (err?.status === 401) {
          this.error = 'Your session has expired. Please sign in again.';
        } else if (err?.status === 403) {
          this.error = 'You do not have permission to view the dashboard.';
        } else {
          this.error =
            'Unable to load dashboard data. Please check the backend connection and try again.';
        }

        this.cdr.detectChanges();
      }
    });
  }
}
