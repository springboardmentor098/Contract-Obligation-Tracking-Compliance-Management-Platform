import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuditService, Activity, AuditLog } from '../services/audit';

@Component({
  selector: 'app-audit-history',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './audit-history.html',
  styleUrl: './audit-history.css'
})
export class AuditHistory implements OnInit {
  activities: Activity[] = [];
  auditLogs: AuditLog[] = [];

  loading = true;
  errorMessage = '';

  constructor(
  private auditService: AuditService,
  private cdr: ChangeDetectorRef
) {}

  ngOnInit(): void {
    this.loadAuditHistory();
  }

  loadAuditHistory(): void {
    this.loading = true;
    this.errorMessage = '';
    this.auditService.getActivities().subscribe({
      next: (data) => {

  this.activities = data;
  this.loadAuditLogs();
},
      error: () => {
        this.errorMessage = 'Unable to load activity history.';
        this.loading = false;
      }
    });
  }

  loadAuditLogs(): void {
    this.auditService.getAuditLogs().subscribe({
    next: (data) => {
    this.auditLogs = data;
    this.loading = false;
    this.cdr.detectChanges();

},
      error: () => {
        this.errorMessage = 'Unable to load audit logs.';
        this.loading = false;
      }
    });
  }
}
