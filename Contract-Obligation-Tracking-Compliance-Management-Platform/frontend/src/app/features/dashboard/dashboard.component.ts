import { Component, inject } from '@angular/core';
import { DashboardService } from '../../core/services/dashboard.service';
import { DashboardSummary } from '../../core/models/models';
import { PageHeaderComponent } from '../../shared/page-header.component';

@Component({
  selector: 'cq-dashboard',
  standalone: true,
  imports: [PageHeaderComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  private readonly service = inject(DashboardService);
  data?: DashboardSummary;
  loading = true;
  error = '';

  constructor() { this.load(); }
  load() {
    this.loading = true; this.error = '';
    this.service.getSummary().subscribe({
      next: data => { this.data = data; this.loading = false; },
      error: err => { this.error = err?.error?.detail || 'Dashboard data could not be loaded from FastAPI.'; this.loading = false; }
    });
  }

  entries(obj: Record<string, number> | undefined) { return Object.entries(obj ?? {}).sort((a,b) => b[1]-a[1]); }
  max(obj: Record<string, number> | undefined) { return Math.max(1, ...Object.values(obj ?? {})); }
}
