import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { finalize } from 'rxjs';
import { DashboardSummary } from '../models';
import { DashboardService } from '../services/dashboard.service';

@Component({ selector: 'app-dashboard', standalone: true, imports: [CommonModule], templateUrl: './dashboard.component.html', styleUrl: './dashboard.component.scss' })
export class DashboardComponent {
  private readonly dashboardService = inject(DashboardService); summary: DashboardSummary | null = null; loading = true; error = '';
  constructor() { this.load(); }
  load(): void { this.loading = true; this.error = ''; this.dashboardService.getSummary().pipe(finalize(() => (this.loading = false))).subscribe({ next: (summary) => (this.summary = summary), error: () => (this.error = 'Dashboard data could not be loaded. Check that the API is running and try again.') }); }
  get contractSegments(): Array<{ label: string; value: number; color: string }> { const contracts = this.summary?.contracts; if (!contracts) return []; return [{ label: 'Active', value: contracts.active, color: '#c7e36b' }, { label: 'Under review', value: contracts.under_review, color: '#ed704b' }, { label: 'Draft', value: contracts.draft, color: '#526255' }, { label: 'Expired', value: contracts.expired, color: '#b8c1b3' }]; }
  get totalContractSegments(): number { return this.contractSegments.reduce((total, segment) => total + segment.value, 0); }
  segmentWidth(value: number): string { return `${this.totalContractSegments ? (value / this.totalContractSegments) * 100 : 0}%`; }
}