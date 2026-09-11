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
  ObligationService,
  ObligationUpdate
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
  statusFilter = '';
  priorityFilter = '';
  typeFilter = '';

  showCreateForm = false;
  showEditForm = false;
  showDetails = false;

  creating = false;
  updating = false;

  createError = '';
  editError = '';

  selectedObligation: Obligation | null = null;

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

  editForm: ObligationUpdate = {
    assigned_to: '',
    title: '',
    description: '',
    obligation_type: '',
    due_date: null,
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
        this.loading = false;
        this.applyFilters();
      },
      error: (error) => {
        console.error('Obligations API error:', error);

        this.loading = false;
        this.error = this.getErrorMessage(
          error,
          'Unable to load obligations. Please try again.'
        );
      }
    });
  }

  applyFilters(): void {
    const search = this.searchTerm.trim().toLowerCase();

    this.filteredObligations = this.obligations.filter(
      (obligation) => {

        const matchesSearch =
          !search ||
          [
            obligation.title,
            obligation.description,
            obligation.obligation_type,
            obligation.priority,
            obligation.status,
            obligation.due_date,
            obligation.contract_id
          ]
            .filter(Boolean)
            .some((value) =>
              String(value).toLowerCase().includes(search)
            );

        const matchesStatus =
          !this.statusFilter ||
          obligation.status === this.statusFilter;

        const matchesPriority =
          !this.priorityFilter ||
          obligation.priority === this.priorityFilter;

        const matchesType =
          !this.typeFilter ||
          obligation.obligation_type === this.typeFilter;

        return (
          matchesSearch &&
          matchesStatus &&
          matchesPriority &&
          matchesType
        );
      }
    );
  }

  onSearch(): void {
    this.applyFilters();
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.statusFilter = '';
    this.priorityFilter = '';
    this.typeFilter = '';

    this.applyFilters();
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

    if (
      this.obligationForm.due_date &&
      !this.isValidDate(this.obligationForm.due_date)
    ) {
      this.createError = 'Please enter a valid due date.';
      return;
    }

    this.creating = true;

    const obligation: ObligationCreate = {
      contract_id:
        this.obligationForm.contract_id.trim(),

      assigned_to:
        this.obligationForm.assigned_to.trim(),

      title:
        this.obligationForm.title.trim(),

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

    this.obligationService
      .createObligation(obligation)
      .subscribe({
        next: () => {
          this.creating = false;
          this.showCreateForm = false;
          this.createError = '';
          this.loadObligations();
        },

        error: (error) => {
          console.error(
            'Create obligation error:',
            error
          );

          this.creating = false;

          this.createError = this.getErrorMessage(
            error,
            'Unable to create obligation. Please try again.'
          );
        }
      });
  }

  viewObligation(obligation: Obligation): void {
    this.selectedObligation = obligation;
    this.showDetails = true;
    this.error = '';
  }

  closeDetails(): void {
    this.showDetails = false;
    this.selectedObligation = null;
  }

  openEditForm(obligation: Obligation): void {
    this.editError = '';

    this.obligationService
      .getObligation(obligation.id)
      .subscribe({
        next: (fullObligation) => {
          this.selectedObligation = fullObligation;

          this.editForm = {
            assigned_to:
              fullObligation.assigned_to,

            title:
              fullObligation.title,

            description:
              fullObligation.description,

            obligation_type:
              fullObligation.obligation_type,

            due_date:
              fullObligation.due_date,

            priority:
              fullObligation.priority || 'Medium'
          };

          this.showEditForm = true;
        },

        error: (error) => {
          console.error(
            'Get obligation error:',
            error
          );

          this.error = this.getErrorMessage(
            error,
            'Unable to load obligation details.'
          );
        }
      });
  }

  closeEditForm(): void {
    if (this.updating) {
      return;
    }

    this.showEditForm = false;
    this.editError = '';
  }

  updateObligation(): void {
    this.editError = '';

    if (!this.selectedObligation) {
      return;
    }

    if (!this.editForm.title?.trim()) {
      this.editError =
        'Obligation title is required.';
      return;
    }

    if (
      this.editForm.due_date &&
      !this.isValidDate(this.editForm.due_date)
    ) {
      this.editError =
        'Please enter a valid due date.';
      return;
    }

    this.updating = true;

    const update: ObligationUpdate = {
      assigned_to:
        this.editForm.assigned_to?.trim() || null,

      title:
        this.editForm.title?.trim() || null,

      description:
        this.editForm.description?.trim() || null,

      obligation_type:
        this.editForm.obligation_type?.trim() || null,

      due_date:
        this.editForm.due_date || null,

      priority:
        this.editForm.priority || null
    };

    this.obligationService
      .updateObligation(
        this.selectedObligation.id,
        update
      )
      .subscribe({
        next: () => {
          this.updating = false;
          this.showEditForm = false;
          this.editError = '';
          this.selectedObligation = null;
          this.loadObligations();
        },

        error: (error) => {
          console.error(
            'Update obligation error:',
            error
          );

          this.updating = false;

          this.editError = this.getErrorMessage(
            error,
            'Unable to update obligation. Please try again.'
          );
        }
      });
  }

  updateStatus(
    obligation: Obligation,
    status: string
  ): void {

    if (
      !status ||
      obligation.status === status
    ) {
      return;
    }

    this.error = '';

    this.obligationService
      .updateStatus(
        obligation.id,
        status
      )
      .subscribe({
        next: () => {
          this.loadObligations();
        },

        error: (error) => {
          console.error(
            'Update obligation status error:',
            error
          );

          this.error = this.getErrorMessage(
            error,
            'Unable to update obligation status.'
          );
        }
      });
  }

  startObligation(
    obligation: Obligation
  ): void {
    this.updateStatus(
      obligation,
      'In Progress'
    );
  }

  completeObligation(
    obligation: Obligation
  ): void {
    this.updateStatus(
      obligation,
      'Completed'
    );
  }

  markDelayed(
    obligation: Obligation
  ): void {
    this.updateStatus(
      obligation,
      'Delayed'
    );
  }

  markOverdue(
    obligation: Obligation
  ): void {
    this.updateStatus(
      obligation,
      'Overdue'
    );
  }

  deleteObligation(
    obligation: Obligation
  ): void {

    const confirmed = window.confirm(
      `Are you sure you want to delete obligation "${obligation.title}"?`
    );

    if (!confirmed) {
      return;
    }

    this.error = '';

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

          this.error = this.getErrorMessage(
            error,
            'Unable to delete obligation.'
          );
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

  canChangeStatus(): boolean {
    return this.canUpdate();
  }

  getStatusClass(
    status: string | null
  ): string {

    if (!status) {
      return 'unknown';
    }

    return status
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  formatDate(
    date: string | null
  ): string {

    if (!date) {
      return 'N/A';
    }

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return date;
    }

    return parsedDate.toLocaleDateString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      }
    );
  }

  formatDateTime(
    date: string | null
  ): string {

    if (!date) {
      return 'N/A';
    }

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return date;
    }

    return parsedDate.toLocaleString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }
    );
  }

  private isValidDate(
    date: string
  ): boolean {

    return !Number.isNaN(
      new Date(date).getTime()
    );
  }

  private getErrorMessage(
    error: any,
    fallback: string
  ): string {

    switch (error?.status) {

      case 400:
        return (
          error.error?.detail ||
          'Invalid obligation information.'
        );

      case 401:
        return 'Your session has expired. Please log in again.';

      case 403:
        return (
          error.error?.detail ||
          'You do not have permission to perform this action.'
        );

      case 404:
        return (
          error.error?.detail ||
          'The requested obligation or related contract/user was not found.'
        );

      case 409:
        return (
          error.error?.detail ||
          'This operation conflicts with the current obligation state.'
        );

      case 422:
        return (
          error.error?.detail ||
          'Please check the entered obligation information.'
        );

      case 500:
        return (
          error.error?.detail ||
          'A server error occurred. Please try again later.'
        );

      case 0:
        return 'Unable to connect to the FastAPI backend. Please make sure the backend is running.';

      default:
        return (
          error?.error?.detail ||
          fallback
        );
    }
  }
}