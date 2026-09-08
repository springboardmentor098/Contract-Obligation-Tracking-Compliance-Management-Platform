import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
  AuditLog,
  AuditLogFilters,
  AuditService
} from '../../services/audit.service';

@Component({
  selector: 'app-audit-history',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatTableModule,
    MatTooltipModule
  ],
  templateUrl: './audit-history.component.html',
  styleUrl: './audit-history.component.scss'
})
export class AuditHistoryComponent implements OnInit {
  private readonly auditService = inject(AuditService);

  auditLogs: AuditLog[] = [];

  loading = true;
  error = '';
  total = 0;

  // Filter values
  entityTypeFilter = '';
  actionFilter = '';
  userIdFilter = '';
  dateFromFilter = '';
  dateToFilter = '';

  // Available filter options
  entityTypes: string[] = [
    'contract',
    'obligation',
    'renewal',
    'compliance',
    'notification',
    'user'
  ];

  actions: string[] = [
    'CREATE',
    'UPDATE',
    'DELETE',
    'APPROVE',
    'ACTIVATE',
    'ASSIGN',
    'COMPLETE',
    'STATUS_CHANGE'
  ];

  displayedColumns: string[] = [
    'action',
    'entity_type',
    'entity_id',
    'user_id',
    'changes',
    'ip_address',
    'created_at'
  ];

  ngOnInit(): void {
    this.loadAuditLogs();
  }

  loadAuditLogs(): void {
    this.loading = true;
    this.error = '';

    const filters: AuditLogFilters = {
      skip: 0,
      limit: 100
    };

    if (this.entityTypeFilter.trim()) {
      filters.entity_type = this.entityTypeFilter.trim();
    }

    if (this.actionFilter.trim()) {
      filters.action = this.actionFilter.trim();
    }

    if (this.userIdFilter.trim()) {
      filters.user_id = this.userIdFilter.trim();
    }

    if (this.dateFromFilter) {
      filters.date_from = this.toStartOfDay(this.dateFromFilter);
    }

    if (this.dateToFilter) {
      filters.date_to = this.toEndOfDay(this.dateToFilter);
    }

    this.auditService.getAuditLogs(filters).subscribe({
      next: (response) => {
        this.auditLogs = response.data;
        this.total = response.total;
        this.loading = false;
      },
      error: (error) => {
        console.error('Audit logs API error:', error);

        this.loading = false;

        this.error = this.getErrorMessage(
          error,
          'Unable to load audit history.'
        );
      }
    });
  }

  applyFilters(): void {
    if (
      this.dateFromFilter &&
      this.dateToFilter &&
      this.dateFromFilter > this.dateToFilter
    ) {
      this.error = 'Date From must be earlier than or equal to Date To.';
      return;
    }

    this.loadAuditLogs();
  }

  clearFilters(): void {
    this.entityTypeFilter = '';
    this.actionFilter = '';
    this.userIdFilter = '';
    this.dateFromFilter = '';
    this.dateToFilter = '';

    this.loadAuditLogs();
  }

  refresh(): void {
    this.loadAuditLogs();
  }

  retry(): void {
    this.loadAuditLogs();
  }

  getActionClass(action: string): string {
    return action
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  getEntityClass(entityType: string): string {
    return entityType
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  formatChanges(log: AuditLog): string {
    const oldValues = log.old_values
      ? JSON.stringify(log.old_values)
      : '';

    const newValues = log.new_values
      ? JSON.stringify(log.new_values)
      : '';

    if (oldValues && newValues) {
      return `Old: ${oldValues} → New: ${newValues}`;
    }

    if (newValues) {
      return `New: ${newValues}`;
    }

    if (oldValues) {
      return `Old: ${oldValues}`;
    }

    return 'No changes recorded';
  }

  formatDate(date: string): string {
    if (!date) {
      return '—';
    }

    return new Date(date).toLocaleString();
  }

  truncateId(id: string): string {
    if (!id) {
      return '—';
    }

    return `${id.substring(0, 8)}...`;
  }

  private toStartOfDay(date: string): string {
    return `${date}T00:00:00`;
  }

  private toEndOfDay(date: string): string {
    return `${date}T23:59:59`;
  }

  private getErrorMessage(
    error: any,
    fallback: string
  ): string {
    if (error?.status === 401) {
      return 'Your session has expired. Please log in again.';
    }

    if (error?.status === 403) {
      return 'You do not have permission to view audit history.';
    }

    if (error?.status === 404) {
      return 'Audit history endpoint was not found on the backend.';
    }

    if (error?.status === 422) {
      return 'Invalid filter values. Please check the entered information.';
    }

    if (error?.status === 0) {
      return 'Unable to connect to the backend. Please make sure FastAPI is running.';
    }

    return error?.error?.detail || fallback;
  }
}