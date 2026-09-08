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
  Renewal,
  RenewalCreate,
  RenewalService
} from '../../services/renewal.service';

import {
  AuthService,
  UserRole
} from '../../services/auth.service';

@Component({
  selector: 'app-renewals',
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
  templateUrl: './renewals.component.html',
  styleUrl: './renewals.component.scss'
})
export class RenewalsComponent implements OnInit {

  private readonly renewalService = inject(RenewalService);
  private readonly authService = inject(AuthService);

  renewals: Renewal[] = [];
  filteredRenewals: Renewal[] = [];

  loading = true;
  error = '';

  searchTerm = '';

  selectedFilter = 'All';

  showCreateForm = false;
  creating = false;
  createError = '';

  showCompleteForm = false;
  completing = false;
  completeError = '';

  selectedRenewal: Renewal | null = null;

  readonly UserRole = UserRole;

  displayedColumns: string[] = [
    'contract_id',
    'renewal_date',
    'previous_expiry_date',
    'new_expiry_date',
    'status',
    'assigned_to',
    'actions'
  ];

  readonly statuses: string[] = [
    'All',
    'Upcoming',
    'In Progress',
    'Renewed',
    'Expired',
    'Cancelled'
  ];

  readonly createStatuses: string[] = [
    'Upcoming',
    'In Progress'
  ];

  renewalForm: RenewalCreate = {
    contract_id: '',
    renewal_date: null,
    previous_expiry_date: null,
    new_expiry_date: null,
    assigned_to: '',
    notes: ''
  };

  newExpiryDate = '';

  ngOnInit(): void {
    this.loadRenewals();
  }

  loadRenewals(): void {
    this.loading = true;
    this.error = '';

    this.renewalService.getRenewals().subscribe({
      next: (renewals) => {
        this.renewals = renewals;
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Renewals API error:', error);

        this.loading = false;

        if (error.status === 401) {
          this.error =
            'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.error =
            'You do not have permission to view these renewals.';
        } else if (error.status === 0) {
          this.error =
            'Unable to connect to the backend. Please make sure FastAPI is running.';
        } else {
          this.error =
            error.error?.detail ||
            'Unable to load renewals. Please try again.';
        }
      }
    });
  }

  onSearch(): void {
    this.applyFilters();
  }

  onFilterChange(): void {
    this.applyFilters();
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.applyFilters();
  }

  applyFilters(): void {
    const search = this.searchTerm
      .trim()
      .toLowerCase();

    this.filteredRenewals = this.renewals.filter(
      (renewal) => {

        const matchesSearch =
          !search ||
          [
            renewal.contract_id,
            renewal.renewal_date,
            renewal.previous_expiry_date,
            renewal.new_expiry_date,
            renewal.status,
            renewal.assigned_to,
            renewal.notes
          ]
            .filter(Boolean)
            .some((value) =>
              String(value)
                .toLowerCase()
                .includes(search)
            );

        const matchesStatus =
          this.selectedFilter === 'All' ||
          renewal.status === this.selectedFilter;

        return matchesSearch && matchesStatus;
      }
    );
  }

  openCreateForm(): void {
    this.createError = '';

    this.renewalForm = {
      contract_id: '',
      renewal_date: null,
      previous_expiry_date: null,
      new_expiry_date: null,
      assigned_to: '',
      notes: ''
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

  createRenewal(): void {
    this.createError = '';

    if (!this.renewalForm.contract_id.trim()) {
      this.createError =
        'Contract ID is required.';
      return;
    }

    if (!this.renewalForm.assigned_to.trim()) {
      this.createError =
        'Assigned user ID is required.';
      return;
    }

    if (
      this.renewalForm.renewal_date &&
      this.renewalForm.previous_expiry_date &&
      this.renewalForm.renewal_date >
        this.renewalForm.previous_expiry_date
    ) {
      this.createError =
        'Renewal date cannot be later than the previous expiry date.';
      return;
    }

    if (
      this.renewalForm.renewal_date &&
      this.renewalForm.new_expiry_date &&
      this.renewalForm.new_expiry_date <
        this.renewalForm.renewal_date
    ) {
      this.createError =
        'New expiry date cannot be earlier than the renewal date.';
      return;
    }

    this.creating = true;

    const renewal: RenewalCreate = {
      contract_id:
        this.renewalForm.contract_id.trim(),

      renewal_date:
        this.renewalForm.renewal_date || null,

      previous_expiry_date:
        this.renewalForm.previous_expiry_date || null,

      new_expiry_date:
        this.renewalForm.new_expiry_date || null,

      assigned_to:
        this.renewalForm.assigned_to.trim(),

      notes:
        this.renewalForm.notes?.trim() || null
    };

    this.renewalService
      .createRenewal(renewal)
      .subscribe({
        next: () => {
          this.creating = false;
          this.showCreateForm = false;
          this.createError = '';
          this.loadRenewals();
        },

        error: (error) => {
          console.error(
            'Create renewal error:',
            error
          );

          this.creating = false;

          if (error.status === 400) {
            this.createError =
              error.error?.detail ||
              'Invalid renewal information.';
          } else if (error.status === 401) {
            this.createError =
              'Your session has expired. Please log in again.';
          } else if (error.status === 403) {
            this.createError =
              'You do not have permission to create renewals.';
          } else if (error.status === 404) {
            this.createError =
              error.error?.detail ||
              'Contract or assigned user was not found.';
          } else if (error.status === 422) {
            this.createError =
              'Please check the required renewal information.';
          } else if (error.status === 0) {
            this.createError =
              'Unable to connect to the backend.';
          } else {
            this.createError =
              error.error?.detail ||
              'Unable to create renewal. Please try again.';
          }
        }
      });
  }

  startRenewal(renewal: Renewal): void {
    if (renewal.status !== 'Upcoming') {
      return;
    }

    this.updateStatus(
      renewal,
      'In Progress'
    );
  }

  updateStatus(
    renewal: Renewal,
    status: string
  ): void {

    if (
      !status ||
      renewal.status === status
    ) {
      return;
    }

    this.renewalService
      .updateStatus(
        renewal.id,
        status
      )
      .subscribe({
        next: () => {
          this.loadRenewals();
        },

        error: (error) => {
          console.error(
            'Update renewal status error:',
            error
          );

          this.error =
            error.error?.detail ||
            'Unable to update renewal status.';
        }
      });
  }

  openCompleteForm(
    renewal: Renewal
  ): void {

    this.selectedRenewal = renewal;

    this.newExpiryDate =
      renewal.new_expiry_date || '';

    this.completeError = '';

    this.showCompleteForm = true;
  }

  closeCompleteForm(): void {
    if (this.completing) {
      return;
    }

    this.showCompleteForm = false;
    this.selectedRenewal = null;
    this.newExpiryDate = '';
    this.completeError = '';
  }

  completeRenewal(): void {

    if (!this.selectedRenewal) {
      return;
    }

    this.completeError = '';

    if (!this.newExpiryDate) {
      this.completeError =
        'New expiry date is required.';
      return;
    }

    if (
      this.selectedRenewal.renewal_date &&
      this.newExpiryDate <
        this.selectedRenewal.renewal_date
    ) {
      this.completeError =
        'New expiry date cannot be earlier than the renewal date.';
      return;
    }

    this.completing = true;

    this.renewalService
      .completeRenewal(
        this.selectedRenewal.id,
        this.newExpiryDate
      )
      .subscribe({
        next: () => {
          this.completing = false;
          this.showCompleteForm = false;
          this.selectedRenewal = null;
          this.newExpiryDate = '';
          this.completeError = '';
          this.loadRenewals();
        },

        error: (error) => {
          console.error(
            'Complete renewal error:',
            error
          );

          this.completing = false;

          if (error.status === 400) {
            this.completeError =
              error.error?.detail ||
              'Unable to complete this renewal.';
          } else if (error.status === 401) {
            this.completeError =
              'Your session has expired. Please log in again.';
          } else if (error.status === 403) {
            this.completeError =
              'You do not have permission to complete this renewal.';
          } else if (error.status === 404) {
            this.completeError =
              'Renewal was not found.';
          } else if (error.status === 0) {
            this.completeError =
              'Unable to connect to the backend.';
          } else {
            this.completeError =
              error.error?.detail ||
              'Unable to complete renewal. Please try again.';
          }
        }
      });
  }

  cancelRenewal(
    renewal: Renewal
  ): void {

    const confirmed = window.confirm(
      `Are you sure you want to cancel the renewal for contract "${renewal.contract_id}"?`
    );

    if (!confirmed) {
      return;
    }

    this.updateStatus(
      renewal,
      'Cancelled'
    );
  }

  markExpired(
    renewal: Renewal
  ): void {

    const confirmed = window.confirm(
      `Mark the renewal for contract "${renewal.contract_id}" as expired?`
    );

    if (!confirmed) {
      return;
    }

    this.updateStatus(
      renewal,
      'Expired'
    );
  }

  canCreate(): boolean {
    return this.authService.hasAnyRole([
      UserRole.ADMINISTRATOR,
      UserRole.LEGAL_MANAGER,
      UserRole.CONTRACT_MANAGER
    ]);
  }

  canUpdate(): boolean {
    return this.authService.hasAnyRole([
      UserRole.ADMINISTRATOR,
      UserRole.LEGAL_MANAGER,
      UserRole.CONTRACT_MANAGER
    ]);
  }

  canComplete(): boolean {
    return this.authService.hasAnyRole([
      UserRole.ADMINISTRATOR,
      UserRole.LEGAL_MANAGER,
      UserRole.CONTRACT_MANAGER
    ]);
  }

  canCancel(): boolean {
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
      return '—';
    }

    return date;
  }
}