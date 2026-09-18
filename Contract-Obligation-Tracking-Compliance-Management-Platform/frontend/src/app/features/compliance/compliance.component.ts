import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

import { ComplianceService } from '../../core/services/compliance.service';
import { ComplianceRecord } from '../../core/models/models';

import { PageHeaderComponent } from '../../shared/page-header.component';
import { StatusComponent } from '../../shared/status.component';
import { EmptyStateComponent } from '../../shared/empty-state.component';

@Component({
  selector: 'cq-compliance',
  standalone: true,
  imports: [
    FormsModule,
    DatePipe,
    PageHeaderComponent,
    StatusComponent,
    EmptyStateComponent
  ],
  templateUrl: './compliance.component.html',
  styleUrl: './compliance.component.css'
})
export class ComplianceComponent {

  private readonly service = inject(ComplianceService);

  items: ComplianceRecord[] = [];
  filtered: ComplianceRecord[] = [];

  status = '';
  loading = true;
  error = '';

  statuses = [
    'Compliant',
    'Pending',
    'Delayed',
    'Non-Compliant',
    'High Risk'
  ];

  constructor() {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';

    this.service.list().subscribe({
      next: (data) => {
        this.items = data ?? [];
        this.apply();
        this.loading = false;
      },
      error: (error) => {
        this.error =
          error?.error?.detail ||
          'Unable to load compliance records.';

        this.loading = false;
      }
    });
  }

  apply(): void {
    this.filtered = this.items.filter(
      item => !this.status || item.status === this.status
    );
  }

  // Dashboard summary counts
  get compliantCount(): number {
    return this.items.filter(
      item => item.status === 'Compliant'
    ).length;
  }

  get pendingCount(): number {
    return this.items.filter(
      item => item.status === 'Pending'
    ).length;
  }

  get delayedCount(): number {
    return this.items.filter(
      item => item.status === 'Delayed'
    ).length;
  }

  get highRiskCount(): number {
    return this.items.filter(
      item =>
        item.status === 'High Risk' ||
        item.status === 'Non-Compliant'
    ).length;
  }
}