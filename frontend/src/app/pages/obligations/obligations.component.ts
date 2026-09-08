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
  Obligation,
  ObligationCreate,
  ObligationService
} from '../../services/obligation.service';

import {
  AuthService,
  UserRole
} from '../../services/auth.service';

@Component({
  selector: 'app-obligations',
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
  templateUrl: './obligations.component.html',
  styleUrl: './obligations.component.scss'
})
export class ObligationsComponent implements OnInit {

  private readonly obligationService = inject(ObligationService);
  private readonly authService = inject(AuthService);

  obligations: Obligation[] = [];
  filteredObligations: Obligation[] = [];

  loading = true;
  error = '';

  searchTerm = '';

  showCreateForm = false;
  creating = false;
  createError = '';

  readonly UserRole = UserRole;

  displayedColumns: string[] = [
    'title',
    'obligation_type',
    'due_date',
    'priority',
    'status',
    'actions'
  ];

  obligationForm: ObligationCreate = {
    contract_id: '',
    assigned_to: '',
    title: '',
    description: '',
    obligation_type: '',
    due_date: null,
    status: 'Pending',
    priority: 'Medium'
  };

  readonly obligationTypes: string[] = [
    'Payment Obligation',
    'Delivery Commitment',
    'Reporting Requirement',
    'Renewal Condition',
    'Service Level Agreement',
    'Legal Compliance Requirement'
  ];

  readonly priorities: string[] = [
    'Low',
    'Medium',
    'High',
    'Critical'
  ];

  readonly statuses: string[] = [
    'Pending',
    'In Progress',
    'Completed',
    'Delayed',
    'Overdue'
  ];

  ngOnInit(): void {
    this.loadObligations();
  }

  loadObligations(): void {
    this.loading = true;
    this.error = '';

    this.obligationService.getObligations().subscribe({
      next: (obligations) => {
        this.obligations = obligations;
        this.filteredObligations = [...obligations];
        this.loading = false;
      },
      error: (error) => {
        console.error('Obligations API error:', error);

        this.loading = false;

        if (error.status === 401) {
          this.error =
            'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.error =
            'You do not have permission to view these obligations.';
        } else if (error.status === 0) {
          this.error =
            'Unable to connect to the backend. Please make sure FastAPI is running.';
        } else {
          this.error =
            error.error?.detail ||
            'Unable to load obligations. Please try again.';
        }
      }
    });
  }

  onSearch(): void {
    const search = this.searchTerm.trim().toLowerCase();

    if (!search) {
      this.filteredObligations = [...this.obligations];
      return;
    }

    this.filteredObligations = this.obligations.filter(
      (obligation) =>
        [
          obligation.title,
          obligation.description,
          obligation.obligation_type,
          obligation.priority,
          obligation.status,
          obligation.due_date
        ]
          .filter(Boolean)
          .some((value) =>
            String(value).toLowerCase().includes(search)
          )
    );
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.filteredObligations = [...this.obligations];
  }

  openCreateForm(): void {
    this.createError = '';

    this.obligationForm = {
      contract_id: '',
      assigned_to: '',
      title: '',
      description: '',
      obligation_type: '',
      due_date: null,
      status: 'Pending',
      priority: 'Medium'
    };

    this.showCreateForm = true;
  }

  closeCreateForm(): void {
    if (this.creating) {
      return;
    }

    this.showCreateForm = false;
    this.createError = '';
  }

  createObligation(): void {
    this.createError = '';

    if (!this.obligationForm.contract_id.trim()) {
      this.createError = 'Contract ID is required.';
      return;
    }

    if (!this.obligationForm.assigned_to.trim()) {
      this.createError = 'Assigned user ID is required.';
      return;
    }

    if (!this.obligationForm.title.trim()) {
      this.createError = 'Obligation title is required.';
      return;
    }

    this.creating = true;

    const obligation: ObligationCreate = {
      contract_id: this.obligationForm.contract_id.trim(),
      assigned_to: this.obligationForm.assigned_to.trim(),
      title: this.obligationForm.title.trim(),
      description:
        this.obligationForm.description?.trim() || null,
      obligation_type:
        this.obligationForm.obligation_type?.trim() || null,
      due_date:
        this.obligationForm.due_date || null,
      status:
        this.obligationForm.status || 'Pending',
      priority:
        this.obligationForm.priority || 'Medium'
    };

    this.obligationService.createObligation(obligation).subscribe({
      next: () => {
        this.creating = false;
        this.showCreateForm = false;
        this.createError = '';
        this.loadObligations();
      },
      error: (error) => {
        console.error('Create obligation error:', error);

        this.creating = false;

        if (error.status === 400) {
          this.createError =
            error.error?.detail ||
            'Invalid obligation information.';
        } else if (error.status === 401) {
          this.createError =
            'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.createError =
            'You do not have permission to create this obligation.';
        } else if (error.status === 404) {
          this.createError =
            error.error?.detail ||
            'Contract or assigned user was not found.';
        } else if (error.status === 422) {
          this.createError =
            'Please check the required obligation information.';
        } else if (error.status === 0) {
          this.createError =
            'Unable to connect to the backend.';
        } else {
          this.createError =
            error.error?.detail ||
            'Unable to create obligation. Please try again.';
        }
      }
    });
  }

  updateStatus(
    obligation: Obligation,
    status: string
  ): void {
    if (!status || obligation.status === status) {
      return;
    }

    this.obligationService
      .updateStatus(obligation.id, status)
      .subscribe({
        next: () => {
          this.loadObligations();
        },
        error: (error) => {
          console.error(
            'Update obligation status error:',
            error
          );

          this.error =
            error.error?.detail ||
            'Unable to update obligation status.';
        }
      });
  }

  completeObligation(obligation: Obligation): void {
    this.updateStatus(obligation, 'Completed');
  }

  deleteObligation(obligation: Obligation): void {
    const confirmed = window.confirm(
      `Are you sure you want to delete obligation "${obligation.title}"?`
    );

    if (!confirmed) {
      return;
    }

    this.obligationService
      .deleteObligation(obligation.id)
      .subscribe({
        next: () => {
          this.loadObligations();
        },
        error: (error) => {
          console.error(
            'Delete obligation error:',
            error
          );

          this.error =
            error.error?.detail ||
            'Unable to delete obligation.';
        }
      });
  }

  canDelete(): boolean {
    return this.authService.hasRole(
      UserRole.ADMINISTRATOR
    );
  }

  canCreate(): boolean {
    return this.authService.hasAnyRole([
      UserRole.ADMINISTRATOR,
      UserRole.LEGAL_MANAGER,
      UserRole.COMPLIANCE_OFFICER,
      UserRole.CONTRACT_MANAGER
    ]);
  }

  canUpdate(): boolean {
    return this.authService.hasAnyRole([
      UserRole.ADMINISTRATOR,
      UserRole.LEGAL_MANAGER,
      UserRole.COMPLIANCE_OFFICER,
      UserRole.CONTRACT_MANAGER,
      UserRole.DEPARTMENT_HEAD,
      UserRole.EMPLOYEE
    ]);
  }

  getStatusClass(status: string | null): string {
    if (!status) {
      return 'unknown';
    }

    return status
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  formatDate(date: string | null): string {
    if (!date) {
      return '—';
    }

    return date;
  }
}