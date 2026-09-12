import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import {
  AuditService,
  AuditLog
} from '../services/audit';


@Component({
  selector: 'app-audit-history',
  standalone: true,

  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ],

  templateUrl: './audit-history.html',
  styleUrl: './audit-history.less'
})
export class AuditHistory implements OnInit {

  // =====================================================
  // DATA
  // =====================================================

  auditLogs: AuditLog[] = [];


  // =====================================================
  // UI STATES
  // =====================================================

  loading = true;

  errorMessage = '';

  isEmpty = false;


  // =====================================================
  // CONSTRUCTOR
  // =====================================================

  constructor(
    private auditService: AuditService,
    private cdr: ChangeDetectorRef
  ) {}


  // =====================================================
  // INITIALIZATION
  // =====================================================

  ngOnInit(): void {
    this.loadAuditLogs();
  }


  // =====================================================
  // LOAD AUDIT LOGS
  // =====================================================

  loadAuditLogs(): void {

    this.loading = true;

    this.errorMessage = '';

    this.isEmpty = false;

    this.auditLogs = [];

    this.cdr.detectChanges();


    this.auditService.getAuditLogs().subscribe({

      // -------------------------------------------------
      // SUCCESS
      // -------------------------------------------------

      next: (data: AuditLog[]) => {

        console.log(
          'Audit Logs:',
          data
        );

        this.auditLogs = data ?? [];

        this.loading = false;

        this.isEmpty =
          this.auditLogs.length === 0;

        this.cdr.detectChanges();
      },


      // -------------------------------------------------
      // ERROR
      // -------------------------------------------------

      error: (error: any) => {

        console.error(
          'Audit Logs Error:',
          error
        );

        this.auditLogs = [];

        this.loading = false;

        this.isEmpty = false;


        if (error?.status === 401) {

          this.errorMessage =
            'Your session has expired. Please login again.';

        }

        else if (error?.status === 403) {

          this.errorMessage =
            'You are not authorized to view audit history.';

        }

        else if (error?.status === 0) {

          this.errorMessage =
            'Unable to connect to the backend server.';

        }

        else {

          this.errorMessage =
            'Failed to load audit history. Please try again.';

        }


        this.cdr.detectChanges();
      }

    });

  }


  // =====================================================
  // REFRESH
  // =====================================================

  refresh(): void {
    this.loadAuditLogs();
  }


  // =====================================================
  // RETRY
  // =====================================================

  retry(): void {
    this.loadAuditLogs();
  }


  // =====================================================
  // ACTION CSS CLASS
  // =====================================================

  getActionClass(action: string): string {

    switch (action?.toUpperCase()) {

      case 'CREATE':
        return 'create';

      case 'UPDATE':
        return 'update';

      case 'DELETE':
        return 'delete';

      case 'LOGIN':
        return 'login';

      default:
        return 'default';
    }

  }


  // =====================================================
  // ACTION ICON
  // =====================================================

  getActionIcon(action: string): string {

    switch (action?.toUpperCase()) {

      case 'CREATE':
        return 'add_circle';

      case 'UPDATE':
        return 'edit';

      case 'DELETE':
        return 'delete';

      case 'LOGIN':
        return 'login';

      default:
        return 'history';
    }

  }


  // =====================================================
  // FORMAT ENTITY TYPE
  // =====================================================

  formatEntityType(
    entityType: string
  ): string {

    if (!entityType) {
      return 'System';
    }

    return entityType
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());

  }


  // =====================================================
  // FORMAT ACTION
  // =====================================================

  formatAction(
    action: string
  ): string {

    if (!action) {
      return 'Action';
    }

    return action
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());

  }


  // =====================================================
  // DETAILS
  // =====================================================

  formatDetails(
    log: AuditLog
  ): string {

    const action =
      this.formatAction(log.action);

    const entity =
      this.formatEntityType(log.entity_type);


    if (
      log.entity_id !== null &&
      log.entity_id !== undefined
    ) {

      return `${action} ${entity} #${log.entity_id}`;

    }


    return `${action} ${entity}`;

  }

}