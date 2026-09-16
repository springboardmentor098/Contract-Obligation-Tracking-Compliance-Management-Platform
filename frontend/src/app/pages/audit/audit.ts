import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import {
  AuditLog,
  AuditService
} from '../../core/services/audit.service';

@Component({
  selector: 'app-audit',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './audit.html',
  styleUrl: './audit.scss'
})
export class Audit implements OnInit {
  private readonly auditService = inject(AuditService);
  private readonly cdr = inject(ChangeDetectorRef);

  auditLogs: AuditLog[] = [];

  loading = true;
  error = '';

  ngOnInit(): void {
    this.loadAuditLogs();
  }

  loadAuditLogs(): void {
    this.loading = true;
    this.error = '';

    this.auditService.getAuditLogs().subscribe({
      next: (response) => {
        this.auditLogs = response?.value ?? [];
        this.loading = false;
        this.cdr.detectChanges();
      },

      error: (err) => {
        console.error('Audit loading error:', err);
        this.error = 'Unable to load audit history.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  get contractActions(): number {
    return this.auditLogs.filter(
      log => log.entity_type === 'Contract'
    ).length;
  }

  get obligationActions(): number {
    return this.auditLogs.filter(
      log => log.entity_type === 'Obligation'
    ).length;
  }

  get renewalActions(): number {
    return this.auditLogs.filter(
      log => log.entity_type === 'Renewal'
    ).length;
  }

  get notificationActions(): number {
    return this.auditLogs.filter(
      log => log.entity_type === 'Notification'
    ).length;
  }

  getActionClass(action: string): string {
    const value = (action || '').toLowerCase();

    if (value.includes('created')) {
      return 'created';
    }

    if (
      value.includes('deleted') ||
      value.includes('expired')
    ) {
      return 'deleted';
    }

    if (
      value.includes('updated') ||
      value.includes('changed') ||
      value.includes('modified')
    ) {
      return 'updated';
    }

    if (value.includes('overdue')) {
      return 'warning';
    }

    return 'default';
  }
}
