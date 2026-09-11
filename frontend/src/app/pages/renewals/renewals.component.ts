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
RenewalUpdate,
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

showDetails = false;
showEditForm = false;
updating = false;
editError = '';

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

editForm: RenewalUpdate = {
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

    this.error = this.getErrorMessage(
      error,
      'Unable to load renewals. Please try again.'
    );
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

clearFilters(): void {
this.searchTerm = '';
this.selectedFilter = 'All';
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

      this.createError = this.getErrorMessage(
        error,
        'Unable to create renewal. Please try again.'
      );
    }
  });

}

viewRenewal(renewal: Renewal): void {
this.error = '';

this.renewalService
  .getRenewal(renewal.id)
  .subscribe({
    next: (fullRenewal) => {
      this.selectedRenewal = fullRenewal;
      this.showDetails = true;
    },

    error: (error) => {
      console.error(
        'Get renewal error:',
        error
      );

      this.error = this.getErrorMessage(
        error,
        'Unable to load renewal details.'
      );
    }
  });

}

closeDetails(): void {
this.showDetails = false;
this.selectedRenewal = null;
}

openEditForm(renewal: Renewal): void {
this.editError = '';

this.renewalService
  .getRenewal(renewal.id)
  .subscribe({
    next: (fullRenewal) => {

      this.selectedRenewal = fullRenewal;

      this.editForm = {
        renewal_date:
          fullRenewal.renewal_date,

        previous_expiry_date:
          fullRenewal.previous_expiry_date,

        new_expiry_date:
          fullRenewal.new_expiry_date,

        assigned_to:
          fullRenewal.assigned_to,

        notes:
          fullRenewal.notes
      };

      this.showEditForm = true;
    },

    error: (error) => {
      console.error(
        'Get renewal for edit error:',
        error
      );

      this.error = this.getErrorMessage(
        error,
        'Unable to load renewal for editing.'
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

updateRenewal(): void {
this.editError = '';

if (!this.selectedRenewal) {
  return;
}

if (
  this.editForm.renewal_date &&
  this.editForm.previous_expiry_date &&
  this.editForm.renewal_date >
    this.editForm.previous_expiry_date
) {
  this.editError =
    'Renewal date cannot be later than the previous expiry date.';
  return;
}

if (
  this.editForm.renewal_date &&
  this.editForm.new_expiry_date &&
  this.editForm.new_expiry_date <
    this.editForm.renewal_date
) {
  this.editError =
    'New expiry date cannot be earlier than the renewal date.';
  return;
}

if (
  this.editForm.new_expiry_date &&
  this.editForm.previous_expiry_date &&
  this.editForm.new_expiry_date <
    this.editForm.previous_expiry_date
) {
  this.editError =
    'New expiry date cannot be earlier than the previous expiry date.';
  return;
}

if (!this.editForm.assigned_to?.trim()) {
  this.editError =
    'Assigned user ID is required.';
  return;
}

this.updating = true;

const update: RenewalUpdate = {
  renewal_date:
    this.editForm.renewal_date || null,

  previous_expiry_date:
    this.editForm.previous_expiry_date || null,

  new_expiry_date:
    this.editForm.new_expiry_date || null,

  assigned_to:
    this.editForm.assigned_to.trim(),

  notes:
    this.editForm.notes?.trim() || null
};

this.renewalService
  .updateRenewal(
    this.selectedRenewal.id,
    update
  )
  .subscribe({
    next: () => {
      this.updating = false;
      this.showEditForm = false;
      this.editError = '';
      this.selectedRenewal = null;
      this.loadRenewals();
    },

    error: (error) => {
      console.error(
        'Update renewal error:',
        error
      );

      this.updating = false;

      this.editError = this.getErrorMessage(
        error,
        'Unable to update renewal. Please try again.'
      );
    }
  });

}

startRenewal(
renewal: Renewal
): void {

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

this.error = '';

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

      this.error = this.getErrorMessage(
        error,
        'Unable to update renewal status.'
      );
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

if (
  this.selectedRenewal.previous_expiry_date &&
  this.newExpiryDate <
    this.selectedRenewal.previous_expiry_date
) {
  this.completeError =
    'New expiry date cannot be earlier than the previous expiry date.';
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

      this.completeError = this.getErrorMessage(
        error,
        'Unable to complete renewal. Please try again.'
      );
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

canMarkExpired(): boolean {
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

private getErrorMessage(
error: any,
fallback: string
): string {

switch (error?.status) {

  case 400:
    return (
      error.error?.detail ||
      'Invalid renewal information.'
    );

  case 401:
    return 'Your session has expired. Please log in again.';

  case 403:
    return (
      error.error?.detail ||
      'You do not have permission to perform this renewal action.'
    );

  case 404:
    return (
      error.error?.detail ||
      'The requested renewal or related contract was not found.'
    );

  case 409:
    return (
      error.error?.detail ||
      'This renewal operation conflicts with the current state.'
    );

  case 422:
    return (
      error.error?.detail ||
      'Please check the entered renewal information.'
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
