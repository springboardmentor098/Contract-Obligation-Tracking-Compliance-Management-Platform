import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';

import {
  Obligation,
  CreateObligationRequest,
  UpdateObligationRequest
} from '../models/obligation.model';

import { ObligationService } from '../services/obligation.service';

@Component({
  selector: 'app-obligations',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule
  ],
  templateUrl: './obligations.html',
  styleUrl: './obligations.css'
})
export class Obligations implements OnInit {
  obligations: Obligation[] = [];

  filteredObligations: Obligation[] = [];

  searchTerm = '';
  selectedStatus = 'All';

  isLoading = false;
  isSaving = false;

  errorMessage = '';
  successMessage = '';

  showForm = false;
  editingObligationId: number | null = null;

  formData: CreateObligationRequest = {
    contract_id: 0,
    title: '',
    description: '',
    obligation_type: '',
    due_date: '',
    assigned_to: null
  };

  statusOptions = [
    'Pending',
    'Completed',
    'Overdue',
    'In Progress'
  ];

  constructor(
    private obligationService: ObligationService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadObligations();
  }

  loadObligations(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.cdr.detectChanges();

    this.obligationService.getObligations().subscribe({
      next: (data) => {
        this.obligations = Array.isArray(data) ? data : [];

        this.applyFilters();

        this.isLoading = false;

        // Force the page to refresh immediately after API data arrives.
        this.cdr.detectChanges();

        console.log(
          'Obligations loaded successfully:',
          this.obligations
        );
        console.log(
          'Filtered obligations:',
          this.filteredObligations
        );
      },

      error: (error) => {
        console.error(
          'Failed to load obligations:',
          error
        );

        this.obligations = [];
        this.filteredObligations = [];

        this.errorMessage =
          this.getErrorMessage(
            error,
            'Unable to load obligations.'
          );

        this.isLoading = false;

        this.cdr.detectChanges();
      }
    });
  }

  applyFilters(): void {
    const search = this.searchTerm
      .trim()
      .toLowerCase();

    this.filteredObligations =
      this.obligations.filter(
        (obligation) => {
          const title =
            String(obligation.title ?? '')
              .toLowerCase();

          const obligationType =
            String(
              obligation.obligation_type ?? ''
            ).toLowerCase();

          const contractId =
            String(obligation.contract_id ?? '');

          const matchesSearch =
            !search ||
            title.includes(search) ||
            obligationType.includes(search) ||
            contractId.includes(search);

          const matchesStatus =
            this.selectedStatus === 'All' ||
            obligation.status === this.selectedStatus;

          return (
            matchesSearch &&
            matchesStatus
          );
        }
      );
  }

  onSearchChange(value: string): void {
    this.searchTerm = value ?? '';

    this.applyFilters();

    this.cdr.detectChanges();
  }

  onStatusFilterChange(value: string): void {
    this.selectedStatus = value ?? 'All';

    this.applyFilters();

    this.cdr.detectChanges();
  }

  openCreateForm(): void {
    this.resetForm();

    this.showForm = true;

    this.errorMessage = '';
    this.successMessage = '';

    this.cdr.detectChanges();
  }

  openEditForm(
    obligation: Obligation
  ): void {
    this.editingObligationId =
      obligation.id;

    this.formData = {
      contract_id: obligation.contract_id,
      title: obligation.title,
      description:
        obligation.description ?? '',
      obligation_type:
        obligation.obligation_type,
      due_date: obligation.due_date,

      // assigned_to is number | null
      assigned_to:
        obligation.assigned_to ?? null
    };

    this.showForm = true;
    this.successMessage = '';
    this.errorMessage = '';

    this.cdr.detectChanges();
  }

  closeForm(): void {
    if (this.isSaving) {
      return;
    }

    this.showForm = false;
    this.editingObligationId = null;

    this.resetForm();

    this.cdr.detectChanges();
  }

  saveObligation(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.isValidForm()) {
      this.errorMessage =
        'Please fill in all required fields.';

      this.cdr.detectChanges();

      return;
    }

    this.isSaving = true;

    this.cdr.detectChanges();

    /*
     * CREATE
     */
    if (
      this.editingObligationId === null
    ) {
      const payload: CreateObligationRequest = {
        contract_id:
          Number(this.formData.contract_id),

        title:
          this.formData.title.trim(),

        description:
          this.formData.description?.trim() ?? '',

        obligation_type:
          this.formData.obligation_type.trim(),

        due_date:
          this.formData.due_date,

        /*
         * FIX:
         * assigned_to is number | null.
         * Do not compare it with ''.
         */
        assigned_to:
          this.formData.assigned_to ?? null
      };

      this.obligationService
        .createObligation(payload)
        .subscribe({
          next: (created) => {
            this.obligations = [
              created,
              ...this.obligations
            ];

            this.applyFilters();

            this.successMessage =
              'Obligation created successfully.';

            this.isSaving = false;
            this.showForm = false;

            this.resetForm();

            this.cdr.detectChanges();
          },

          error: (error) => {
            console.error(
              'Failed to create obligation:',
              error
            );

            this.errorMessage =
              this.getErrorMessage(
                error,
                'Unable to create obligation.'
              );

            this.isSaving = false;

            this.cdr.detectChanges();
          }
        });

      return;
    }

    /*
     * UPDATE
     */
    const updatePayload:
      UpdateObligationRequest = {
      title:
        this.formData.title.trim(),

      description:
        this.formData.description?.trim() ?? '',

      obligation_type:
        this.formData.obligation_type.trim(),

      due_date:
        this.formData.due_date,

      /*
       * FIX:
       * assigned_to is number | null.
       * Do not compare it with ''.
       */
      assigned_to:
        this.formData.assigned_to ?? null
    };

    this.obligationService
      .updateObligation(
        this.editingObligationId,
        updatePayload
      )
      .subscribe({
        next: (updated) => {
          this.obligations =
            this.obligations.map(
              (item) =>
                item.id === updated.id
                  ? updated
                  : item
            );

          this.applyFilters();

          this.successMessage =
            'Obligation updated successfully.';

          this.isSaving = false;
          this.showForm = false;
          this.editingObligationId = null;

          this.resetForm();

          this.cdr.detectChanges();
        },

        error: (error) => {
          console.error(
            'Failed to update obligation:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to update obligation.'
            );

          this.isSaving = false;

          this.cdr.detectChanges();
        }
      });
  }

  viewObligation(
    obligation: Obligation
  ): void {
    this.errorMessage = '';

    this.obligationService
      .getObligation(obligation.id)
      .subscribe({
        next: (details) => {
          window.alert(
            [
              `ID: ${details.id}`,
              `Title: ${details.title}`,
              `Contract ID: ${details.contract_id}`,
              `Type: ${details.obligation_type}`,
              `Due Date: ${details.due_date}`,
              `Status: ${details.status}`,
              `Assigned To: ${
                details.assigned_to ??
                'Not assigned'
              }`,
              `Description: ${
                details.description ??
                'No description'
              }`
            ].join('\n')
          );

          this.cdr.detectChanges();
        },

        error: (error) => {
          console.error(
            'Failed to load obligation details:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to load obligation details.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  changeStatus(
    obligation: Obligation,
    status: string
  ): void {
    if (
      !status ||
      status === obligation.status
    ) {
      return;
    }

    this.errorMessage = '';
    this.successMessage = '';

    this.obligationService
      .updateStatus(
        obligation.id,
        { status }
      )
      .subscribe({
        next: (updated) => {
          this.obligations =
            this.obligations.map(
              (item) =>
                item.id === updated.id
                  ? updated
                  : item
            );

          this.applyFilters();

          this.successMessage =
            'Obligation status updated successfully.';

          this.cdr.detectChanges();
        },

        error: (error) => {
          console.error(
            'Failed to update obligation status:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to update obligation status.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  completeObligation(
    obligation: Obligation
  ): void {
    if (
      obligation.status === 'Completed'
    ) {
      return;
    }

    this.errorMessage = '';
    this.successMessage = '';

    this.obligationService
      .completeObligation(obligation.id)
      .subscribe({
        next: (updated) => {
          this.obligations =
            this.obligations.map(
              (item) =>
                item.id === updated.id
                  ? updated
                  : item
            );

          this.applyFilters();

          this.successMessage =
            'Obligation marked as completed.';

          this.cdr.detectChanges();
        },

        error: (error) => {
          console.error(
            'Failed to complete obligation:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to complete obligation.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  getStatusClass(
    status: string
  ): string {
    return String(status ?? '')
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  isOverdue(
    obligation: Obligation
  ): boolean {
    if (
      obligation.status === 'Completed'
    ) {
      return false;
    }

    if (!obligation.due_date) {
      return false;
    }

    const dueDate = new Date(
      `${obligation.due_date}T00:00:00`
    );

    const today = new Date();

    today.setHours(
      0,
      0,
      0,
      0
    );

    return dueDate < today;
  }

  private isValidForm(): boolean {
    return (
      Number(this.formData.contract_id) > 0 &&
      this.formData.title.trim().length > 0 &&
      this.formData.obligation_type.trim().length > 0 &&
      this.formData.due_date.length > 0
    );
  }

  private resetForm(): void {
    this.formData = {
      contract_id: 0,
      title: '',
      description: '',
      obligation_type: '',
      due_date: '',
      assigned_to: null
    };

    this.editingObligationId = null;
    this.isSaving = false;
  }

  private getErrorMessage(
    error: any,
    fallback: string
  ): string {
    if (error?.status === 401) {
      return (
        'Your session is not authorized. ' +
        'Please log in again.'
      );
    }

    if (error?.status === 403) {
      return (
        'You are not authorized to perform this action.'
      );
    }

    if (error?.status === 404) {
      return (
        'The requested obligation was not found.'
      );
    }

    if (error?.status === 422) {
      return (
        'Some entered data is invalid. ' +
        'Please check the form.'
      );
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