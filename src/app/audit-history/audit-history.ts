import { CommonModule } from '@angular/common';
import {
  Component,
  OnInit,
  ChangeDetectorRef
} from '@angular/core';

import { HttpErrorResponse } from '@angular/common/http';
import { finalize } from 'rxjs';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';

import { AuditHistoryService } from '../services/audit-history.service';
import { AuditLog } from '../models/audit-history.model';

@Component({
  selector: 'app-audit-history',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatButtonModule
  ],
  templateUrl: './audit-history.html',
  styleUrl: './audit-history.css'
})
export class AuditHistory implements OnInit {

  auditLogs: AuditLog[] = [];

  loading = false;
  errorMessage = '';

  constructor(
    private readonly auditHistoryService: AuditHistoryService,
    private readonly cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadAuditHistory();
  }

  loadAuditHistory(): void {

    this.loading = true;
    this.errorMessage = '';

    this.cdr.detectChanges();

    console.log(
      'Audit History: loading started'
    );

    this.auditHistoryService
      .getAuditLogs()
      .pipe(
        finalize(() => {

          this.loading = false;

          console.log(
            'Audit History: loading finished =',
            this.loading
          );

          this.cdr.detectChanges();
        })
      )
      .subscribe({

        next: (data: AuditLog[]) => {

          console.log(
            'Audit History: received',
            data
          );

          this.auditLogs =
            Array.isArray(data)
              ? data
              : [];

          this.cdr.detectChanges();
        },

        error: (error: HttpErrorResponse) => {

          console.error(
            'Audit History API error:',
            error
          );

          this.auditLogs = [];

          if (error.status === 401) {

            this.errorMessage =
              'Your session has expired. Please log in again.';

          } else if (error.status === 403) {

            this.errorMessage =
              'You are not authorized to view audit history.';

          } else {

            this.errorMessage =
              error.error?.detail ??
              'Failed to load audit history.';
          }

          this.cdr.detectChanges();
        }
      });
  }

  formatJson(
    value: Record<string, unknown> | null
  ): string {

    if (
      value === null ||
      value === undefined
    ) {
      return '—';
    }

    try {

      return JSON.stringify(
        value,
        null,
        2
      );

    } catch {

      return String(value);
    }
  }

  getActionIcon(
    action: string
  ): string {

    const normalized =
      action.toLowerCase();

    if (
      normalized.includes('create')
    ) {
      return 'add_circle';
    }

    if (
      normalized.includes('update') ||
      normalized.includes('edit')
    ) {
      return 'edit';
    }

    if (
      normalized.includes('delete')
    ) {
      return 'delete';
    }

    if (
      normalized.includes('approve') ||
      normalized.includes('activate')
    ) {
      return 'check_circle';
    }

    return 'history';
  }

  refresh(): void {
    this.loadAuditHistory();
  }
}