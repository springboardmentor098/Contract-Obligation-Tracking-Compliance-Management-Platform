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
  Contract,
  CreateContractRequest,
  UpdateContractRequest
} from '../models/contract.model';

import { ContractService } from '../services/contract.service';

@Component({
  selector: 'app-contracts',
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
  templateUrl: './contracts.html',
  styleUrl: './contracts.css'
})
export class Contracts implements OnInit {

  private readonly contractService =
    inject(ContractService);

  private readonly fb =
    inject(FormBuilder);

  private readonly cdr =
    inject(ChangeDetectorRef);

  contracts: Contract[] = [];

  filteredContracts: Contract[] = [];

  selectedContract: Contract | null = null;

  loading = false;

  saving = false;

  errorMessage = '';

  successMessage = '';

  searchText = '';

  statusFilter = 'ALL';

  isEditMode = false;

  editingId: number | null = null;

  showForm = false;

  readonly statuses = [
    'Draft',
    'Under Review',
    'Approved',
    'Active',
    'Expired',
    'Terminated'
  ];

  readonly categories = [
    'Employment Contracts',
    'Vendor Contracts',
    'Service Agreements',
    'Lease Agreements',
    'Purchase Agreements',
    'Partnership Agreements',
    'Confidentiality Agreements',
    'IT Services',
    'Procurement',
    'Training',
    'Service',
    'Lease Agreement',
    'Vendor Contract'
  ];

  contractForm = this.fb.group({
    title: ['', Validators.required],
    contract_number: ['', Validators.required],
    category: ['', Validators.required],
    description: [''],
    start_date: ['', Validators.required],
    end_date: ['', Validators.required]
  });

  ngOnInit(): void {
    this.loadContracts();
  }

  loadContracts(): void {
    this.loading = true;
    this.errorMessage = '';

    this.contractService.getContracts().subscribe({

      next: (data) => {

        console.log(
          'Contracts API response:',
          data
        );

        this.contracts =
          Array.isArray(data)
            ? data
            : [];

        this.applyFilters();

        this.loading = false;

        this.cdr.detectChanges();
      },

      error: (error) => {

        console.error(
          'Contracts API error:',
          error
        );

        this.contracts = [];

        this.filteredContracts = [];

        this.loading = false;

        this.errorMessage =
          this.getErrorMessage(
            error,
            'Unable to load contracts.'
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

    this.filteredContracts =
      this.contracts.filter(
        (contract) => {

          const matchesSearch =
            !search ||
            String(
              contract.title ?? ''
            )
              .toLowerCase()
              .includes(search) ||
            String(
              contract.contract_number ?? ''
            )
              .toLowerCase()
              .includes(search) ||
            String(
              contract.category ?? ''
            )
              .toLowerCase()
              .includes(search);

          const matchesStatus =
            this.statusFilter === 'ALL' ||
            contract.status ===
              this.statusFilter;

          return (
            matchesSearch &&
            matchesStatus
          );
        }
      );
  }

  onSearchChange(value: string): void {
    this.searchText = value;
    this.applyFilters();
    this.cdr.detectChanges();
  }

  onStatusFilterChange(value: string): void {
    this.statusFilter = value;
    this.applyFilters();
    this.cdr.detectChanges();
  }

  openCreateForm(): void {

    this.isEditMode = false;

    this.editingId = null;

    this.selectedContract = null;

    this.successMessage = '';

    this.errorMessage = '';

    this.contractForm.reset();

    this.showForm = true;

    this.cdr.detectChanges();
  }

  openEditForm(
    contract: Contract
  ): void {

    this.isEditMode = true;

    this.editingId =
      contract.id;

    this.selectedContract = null;

    this.successMessage = '';

    this.errorMessage = '';

    this.contractForm.patchValue({
      title: contract.title,
      contract_number:
        contract.contract_number,
      category: contract.category,
      description:
        contract.description ?? '',
      start_date:
        contract.start_date,
      end_date:
        contract.end_date ?? ''
    });

    this.showForm = true;

    this.cdr.detectChanges();
  }

  cancelForm(): void {

    this.showForm = false;

    this.isEditMode = false;

    this.editingId = null;

    this.contractForm.reset();

    this.errorMessage = '';

    this.cdr.detectChanges();
  }

  saveContract(): void {

    this.successMessage = '';

    this.errorMessage = '';

    if (this.contractForm.invalid) {

      this.contractForm.markAllAsTouched();

      this.errorMessage =
        'Please fill in all required contract fields.';

      this.cdr.detectChanges();

      return;
    }

    this.saving = true;

    if (
      this.isEditMode &&
      this.editingId !== null
    ) {

      const request:
        UpdateContractRequest = {

        title:
          this.contractForm.value.title ??
          '',

        category:
          this.contractForm.value.category ??
          '',

        description:
          this.contractForm.value.description ??
          '',

        start_date:
          this.contractForm.value.start_date ??
          '',

        end_date:
          this.contractForm.value.end_date ??
          ''
      };

      this.contractService
        .updateContract(
          this.editingId,
          request
        )
        .subscribe({

          next: (
            updatedContract
          ) => {

            this.saving = false;

            this.successMessage =
              'Contract updated successfully.';

            this.showForm = false;

            this.isEditMode = false;

            this.editingId = null;

            this.contractForm.reset();

            this.selectedContract =
              updatedContract;

            this.loadContracts();

            this.cdr.detectChanges();
          },

          error: (error) => {

            this.saving = false;

            console.error(
              'Update contract error:',
              error
            );

            this.errorMessage =
              this.getErrorMessage(
                error,
                'Unable to update contract.'
              );

            this.cdr.detectChanges();
          }
        });

      return;
    }

    const request:
      CreateContractRequest = {

      title:
        this.contractForm.value.title ??
        '',

      contract_number:
        this.contractForm.value.contract_number ??
        '',

      category:
        this.contractForm.value.category ??
        '',

      description:
        this.contractForm.value.description ??
        '',

      start_date:
        this.contractForm.value.start_date ??
        '',

      end_date:
        this.contractForm.value.end_date ??
        ''
    };

    this.contractService
      .createContract(request)
      .subscribe({

        next: (
          createdContract
        ) => {

          this.saving = false;

          this.successMessage =
            'Contract created successfully.';

          this.showForm = false;

          this.contractForm.reset();

          this.selectedContract =
            createdContract;

          this.loadContracts();

          this.cdr.detectChanges();
        },

        error: (error) => {

          this.saving = false;

          console.error(
            'Create contract error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to create contract.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  viewContract(
    contract: Contract
  ): void {

    this.errorMessage = '';

    this.successMessage = '';

    this.contractService
      .getContract(contract.id)
      .subscribe({

        next: (data) => {

          this.selectedContract =
            data;

          this.showForm = false;

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Get contract details error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to load contract details.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  closeDetails(): void {

    this.selectedContract = null;

    this.cdr.detectChanges();
  }

  deleteContract(
    contract: Contract
  ): void {

    const confirmed =
      window.confirm(
        `Delete contract "${contract.contract_number}"?`
      );

    if (!confirmed) {
      return;
    }

    this.errorMessage = '';

    this.successMessage = '';

    this.contractService
      .deleteContract(contract.id)
      .subscribe({

        next: () => {

          this.successMessage =
            'Contract deleted successfully.';

          this.selectedContract = null;

          this.loadContracts();

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Delete contract error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to delete contract.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  changeStatus(
    contract: Contract,
    status: string
  ): void {

    if (
      !status ||
      status === contract.status
    ) {
      return;
    }

    this.errorMessage = '';

    this.successMessage = '';

    this.contractService
      .updateStatus(
        contract.id,
        status
      )
      .subscribe({

        next: (
          updatedContract
        ) => {

          this.successMessage =
            'Contract status updated successfully.';

          this.selectedContract =
            updatedContract;

          this.loadContracts();

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Status update error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to update contract status.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  submitForReview(
    contract: Contract
  ): void {

    this.errorMessage = '';

    this.successMessage = '';

    this.contractService
      .submitForReview(contract.id)
      .subscribe({

        next: (
          updatedContract
        ) => {

          this.successMessage =
            'Contract submitted for review.';

          this.selectedContract =
            updatedContract;

          this.loadContracts();

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Submit for review error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to submit contract for review.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  approveContract(
    contract: Contract
  ): void {

    this.errorMessage = '';

    this.successMessage = '';

    this.contractService
      .approve(contract.id)
      .subscribe({

        next: (
          updatedContract
        ) => {

          this.successMessage =
            'Contract approved successfully.';

          this.selectedContract =
            updatedContract;

          this.loadContracts();

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Approve contract error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to approve contract.'
            );

          this.cdr.detectChanges();
        }
      });
  }

  activateContract(
    contract: Contract
  ): void {

    this.errorMessage = '';

    this.successMessage = '';

    this.contractService
      .activate(contract.id)
      .subscribe({

        next: (
          updatedContract
        ) => {

          this.successMessage =
            'Contract activated successfully.';

          this.selectedContract =
            updatedContract;

          this.loadContracts();

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error(
            'Activate contract error:',
            error
          );

          this.errorMessage =
            this.getErrorMessage(
              error,
              'Unable to activate contract.'
            );

          this.cdr.detectChanges();
        }
      });
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
      return 'The requested contract was not found.';
    }

    if (error?.status === 409) {
      return 'A contract with the same information already exists.';
    }

    if (error?.status === 422) {
      return 'Please check the entered contract details.';
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