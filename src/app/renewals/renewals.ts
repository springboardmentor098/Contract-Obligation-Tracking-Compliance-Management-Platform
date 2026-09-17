import {
  Component,
  OnInit,
  ChangeDetectorRef,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import {
  Renewal,
  CreateRenewalRequest,
  UpdateRenewalRequest
} from '../models/renewal.model';

import { RenewalService } from '../services/renewal.service';

@Component({
  selector: 'app-renewals',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './renewals.html',
  styleUrl: './renewals.css'
})
export class Renewals implements OnInit {

  private readonly renewalService =
    inject(RenewalService);

  private readonly fb =
    inject(FormBuilder);

  private readonly cdr =
    inject(ChangeDetectorRef);

  renewals: Renewal[] = [];

  filteredRenewals: Renewal[] = [];

  selectedRenewal: Renewal | null = null;

  loading = false;

  saving = false;

  showForm = false;

  isEditMode = false;

  editingId: number | null = null;

  searchText = '';

  statusFilter = 'ALL';

  viewFilter = 'ALL';

  errorMessage = '';

  successMessage = '';

  readonly statuses = [
    'Pending',
    'In Progress',
    'Renewed',
    'Expired',
    'Cancelled'
  ];

  renewalForm = this.fb.group({

    contract_id: [
      0,
      [
        Validators.required,
        Validators.min(1)
      ]
    ],

    renewal_date: [
      '',
      Validators.required
    ],

    previous_expiry_date: [
      '',
      Validators.required
    ],

    new_expiry_date: [
      '',
      Validators.required
    ],

    status: [
      'Pending',
      Validators.required
    ],

    assigned_to: [
      null as number | null
    ],

    notes: [
      ''
    ]
  });

  ngOnInit(): void {
    this.loadRenewals();
  }

  loadRenewals(): void {

    this.loading = true;

    this.errorMessage = '';

    this.renewalService
      .getRenewals()
      .subscribe({

        next: (data) => {

          console.log(
            'Renewals API response:',
            data
          );

          this.renewals =
            Array.isArray(data)
              ? data
              : [];

          this.applyFilters();

          this.loading = false;

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Renewals API error:',
            error
          );

          this.renewals = [];

          this.filteredRenewals = [];

          this.loading = false;

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to load renewals.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  applyFilters(): void {

    const search =
      this.searchText
        .trim()
        .toLowerCase();

    this.filteredRenewals =
      this.renewals.filter(
        (renewal) => {

          const matchesSearch =
            !search ||
            String(
              renewal.contract_id
            )
              .includes(search) ||
            String(
              renewal.status ?? ''
            )
              .toLowerCase()
              .includes(search) ||
            String(
              renewal.notes ?? ''
            )
              .toLowerCase()
              .includes(search);

          const matchesStatus =
            this.statusFilter === 'ALL' ||
            renewal.status ===
              this.statusFilter;

          const matchesView =
            this.matchesViewFilter(
              renewal
            );

          return (
            matchesSearch &&
            matchesStatus &&
            matchesView
          );
        }
      );
  }

  private matchesViewFilter(
    renewal: Renewal
  ): boolean {

    if (
      this.viewFilter ===
      'UPCOMING'
    ) {
      return this.isUpcoming(
        renewal
      );
    }

    if (
      this.viewFilter ===
      'EXPIRED'
    ) {
      return this.isExpired(
        renewal
      );
    }

    return true;
  }

  onSearchChange(
    value: string
  ): void {

    this.searchText = value;

    this.applyFilters();

    this.cdr.detectChanges();
  }

  onStatusFilterChange(
    value: string
  ): void {

    this.statusFilter = value;

    this.applyFilters();

    this.cdr.detectChanges();
  }

  onViewFilterChange(
    value: string
  ): void {

    this.viewFilter = value;

    this.applyFilters();

    this.cdr.detectChanges();
  }

  openCreateForm(): void {

    this.isEditMode = false;

    this.editingId = null;

    this.selectedRenewal = null;

    this.showForm = true;

    this.errorMessage = '';

    this.successMessage = '';

    this.renewalForm.reset({

      contract_id: 0,

      renewal_date: '',

      previous_expiry_date: '',

      new_expiry_date: '',

      status: 'Pending',

      assigned_to: null,

      notes: ''
    });

    this.cdr.detectChanges();
  }

  openEditForm(
    renewal: Renewal
  ): void {

    this.isEditMode = true;

    this.editingId =
      renewal.id;

    this.selectedRenewal = null;

    this.showForm = true;

    this.errorMessage = '';

    this.successMessage = '';

    this.renewalForm.patchValue({

      contract_id:
        renewal.contract_id,

      renewal_date:
        renewal.renewal_date,

      previous_expiry_date:
        renewal.previous_expiry_date,

      new_expiry_date:
        renewal.new_expiry_date,

      status:
        renewal.status,

      assigned_to:
        renewal.assigned_to,

      notes:
        renewal.notes ?? ''
    });

    this.cdr.detectChanges();
  }

  cancelForm(): void {

    this.showForm = false;

    this.isEditMode = false;

    this.editingId = null;

    this.renewalForm.reset({

      contract_id: 0,

      renewal_date: '',

      previous_expiry_date: '',

      new_expiry_date: '',

      status: 'Pending',

      assigned_to: null,

      notes: ''
    });

    this.errorMessage = '';

    this.cdr.detectChanges();
  }

  saveRenewal(): void {

    this.errorMessage = '';

    this.successMessage = '';

    if (
      this.renewalForm.invalid
    ) {

      this.renewalForm
        .markAllAsTouched();

      this.errorMessage =
        'Please fill in all required renewal fields.';

      this.cdr.detectChanges();

      return;
    }

    this.saving = true;

    const formValue =
      this.renewalForm
        .getRawValue();

    if (
      formValue.contract_id === null ||
      formValue.contract_id <= 0
    ) {

      this.saving = false;

      this.errorMessage =
        'Please enter a valid Contract ID.';

      this.cdr.detectChanges();

      return;
    }

    const assignedTo =
      formValue.assigned_to === null ||
      formValue.assigned_to === undefined
        ? null
        : Number(
            formValue.assigned_to
          );

    if (
      formValue.renewal_date &&
      formValue.previous_expiry_date &&
      formValue.new_expiry_date &&
      formValue.new_expiry_date <
        formValue.previous_expiry_date
    ) {

      this.saving = false;

      this.errorMessage =
        'New expiry date cannot be earlier than the previous expiry date.';

      this.cdr.detectChanges();

      return;
    }

    if (
      this.isEditMode &&
      this.editingId !== null
    ) {

      const request:
        UpdateRenewalRequest = {

        contract_id:
          Number(
            formValue.contract_id
          ),

        renewal_date:
          formValue.renewal_date ??
          '',

        previous_expiry_date:
          formValue.previous_expiry_date ??
          '',

        new_expiry_date:
          formValue.new_expiry_date ??
          '',

        status:
          formValue.status ??
          'Pending',

        assigned_to:
          assignedTo,

        notes:
          formValue.notes ??
          ''
      };

      this.renewalService
        .updateRenewal(
          this.editingId,
          request
        )
        .subscribe({

          next: (
            updatedRenewal
          ) => {

            this.saving = false;

            this.successMessage =
              'Renewal updated successfully.';

            this.showForm = false;

            this.isEditMode = false;

            this.editingId = null;

            this.selectedRenewal =
              updatedRenewal;

            this.loadRenewals();

            this.cdr.detectChanges();
          },

          error: (error) => {

            this.saving = false;

            console.error(
              'Update renewal error:',
              error
            );

            this.errorMessage =
              this.getErrorMessage(
                error,
                'Unable to update renewal.'
              );

            this.cdr.detectChanges();
          }
        });

      return;
    }

    const request:
      CreateRenewalRequest = {

      contract_id:
        Number(
          formValue.contract_id
        ),

      renewal_date:
        formValue.renewal_date ??
        '',

      previous_expiry_date:
        formValue.previous_expiry_date ??
        '',

      new_expiry_date:
        formValue.new_expiry_date ??
        '',

      status:
        formValue.status ??
        'Pending',

      assigned_to:
        assignedTo,

      notes:
        formValue.notes ??
        ''
    };

    this.renewalService
      .createRenewal(request)
      .subscribe({

        next: (
          createdRenewal
        ) => {

          this.saving = false;

          this.successMessage =
            'Renewal created successfully.';

          this.showForm = false;

          this.selectedRenewal =
            createdRenewal;

          this.loadRenewals();

          this.cdr.detectChanges();
        },

        error: (error) => {

          this.saving = false;

          console.error(
            'Create renewal error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to create renewal.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  viewRenewal(
    renewal: Renewal
  ): void {

    this.errorMessage = '';

    this.successMessage = '';

    this.renewalService
      .getRenewal(renewal.id)
      .subscribe({

        next: (data) => {

          this.selectedRenewal =
            data;

          this.showForm = false;

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Get renewal details error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to load renewal details.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  closeDetails(): void {

    this.selectedRenewal = null;

    this.cdr.detectChanges();
  }

  deleteRenewal(
    renewal: Renewal
  ): void {

    const confirmed =
      window.confirm(
        `Delete renewal for contract #${renewal.contract_id}?`
      );

    if (!confirmed) {
      return;
    }

    this.errorMessage = '';

    this.successMessage = '';

    this.renewalService
      .deleteRenewal(
        renewal.id
      )
      .subscribe({

        next: () => {

          this.successMessage =
            'Renewal deleted successfully.';

          this.selectedRenewal =
            null;

          this.loadRenewals();

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Delete renewal error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to delete renewal.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  changeStatus(
    renewal: Renewal,
    status: string
  ): void {

    if (
      !status ||
      status === renewal.status
    ) {
      return;
    }

    this.errorMessage = '';

    this.successMessage = '';

    this.renewalService
      .updateStatus(
        renewal.id,
        { status }
      )
      .subscribe({

        next: (
          updatedRenewal
        ) => {

          this.successMessage =
            'Renewal status updated successfully.';

          this.selectedRenewal =
            updatedRenewal;

          this.loadRenewals();

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Update renewal status error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to update renewal.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  renewContract(
    renewal: Renewal
  ): void {

    const confirmed =
      window.confirm(
        `Complete renewal for contract #${renewal.contract_id}?`
      );

    if (!confirmed) {
      return;
    }

    this.errorMessage = '';

    this.successMessage = '';

    this.renewalService
      .renew(
        renewal.id
      )
      .subscribe({

        next: (
          updatedRenewal
        ) => {

          this.successMessage =
            'Renewal completed successfully.';

          this.selectedRenewal =
            updatedRenewal;

          this.loadRenewals();

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Complete renewal error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to complete renewal.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  isUpcoming(
    renewal: Renewal
  ): boolean {

    if (
      renewal.status ===
        'Renewed' ||
      renewal.status ===
        'Expired'
    ) {
      return false;
    }

    const renewalDate =
      new Date(
        `${renewal.renewal_date}T00:00:00`
      );

    const today =
      new Date();

    today.setHours(
      0,
      0,
      0,
      0
    );

    return renewalDate >= today;
  }

  isExpired(
    renewal: Renewal
  ): boolean {

    if (
      renewal.status ===
      'Renewed'
    ) {
      return false;
    }

    const dateToCheck =
      new Date(
        `${renewal.renewal_date}T00:00:00`
      );

    const today =
      new Date();

    today.setHours(
      0,
      0,
      0,
      0
    );

    return dateToCheck < today;
  }

  getStatusClass(
    status: string
  ): string {

    return String(
      status ?? ''
    )
      .toLowerCase()
      .replace(
        /\s+/g,
        '-'
      );
  }

  getErrorMessage(
    error: any,
    fallback: string
  ): string {

    if (error?.status === 401) {
      return 'Your session has expired. Please log in again.';
    }

    if (error?.status === 403) {
      return 'You are not authorized to perform this action.';
    }

    if (error?.status === 404) {
      return 'The requested renewal was not found.';
    }

    if (error?.status === 409) {
      return 'A renewal with the same information already exists.';
    }

    if (error?.status === 422) {
      return 'Please check the entered renewal details.';
    }

    if (error?.status >= 500) {
      return 'The server encountered an error. Please try again.';
    }

    if (
      error?.error?.detail &&
      typeof error.error.detail === 'string'
    ) {
      return error.error.detail;
    }

    return fallback;
  }
}