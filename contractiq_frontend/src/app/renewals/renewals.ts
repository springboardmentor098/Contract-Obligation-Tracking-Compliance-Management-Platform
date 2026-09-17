import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatSelectModule } from '@angular/material/select';

import {
  RenewalsService,
  Renewal,
  RenewalCreate
} from '../services/renewals';

import {
  ContractsService,
  Contract
} from '../services/contracts';

@Component({
  selector: 'app-renewals',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatTableModule,
    MatSelectModule
  ],
  templateUrl: './renewals.html',
  styleUrl: './renewals.css'
})
export class Renewals implements OnInit {

  renewals: Renewal[] = [];
  filteredRenewals: Renewal[] = [];
  contracts: Contract[] = [];

  loading = false;
  saving = false;

  errorMessage = '';
  successMessage = '';

  searchText = '';
  selectedStatus = '';

  showForm = false;
  editingRenewal: Renewal | null = null;
  selectedRenewal: Renewal | null = null;

  displayedColumns = [
    'contract_id',
    'renewal_date',
    'previous_expiry_date',
    'new_expiry_date',
    'renewal_status',
    'assigned_to',
    'actions'
  ];

  statuses = [
    'Upcoming',
    'In Progress',
    'Renewed',
    'Expired',
    'Cancelled'
  ];

  renewalForm!: FormGroup;

  constructor(
    private formBuilder: FormBuilder,
    private renewalsService: RenewalsService,
    private contractsService: ContractsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {

    this.renewalForm = this.formBuilder.group({
      contract_id: ['', Validators.required],
      renewal_date: ['', Validators.required],
      previous_expiry_date: ['', Validators.required],
      new_expiry_date: ['', Validators.required],
      assigned_to: [''],
      notes: ['']
    });

    this.loadContracts();
    this.loadRenewals();
  }

  loadContracts(): void {

    this.contractsService.getContracts().subscribe({
      next: (data) => {
        this.contracts = data;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Contracts API error:', error);
      }
    });
  }

  loadRenewals(): void {

    this.loading = true;
    this.errorMessage = '';

    this.renewalsService.getRenewals().subscribe({

      next: (data) => {

        this.renewals = data;
        this.applyFilters();

        this.loading = false;

        this.cdr.markForCheck();
      },

      error: (error) => {

        console.error('Renewals API error:', error);

        this.errorMessage =
          'Unable to load renewals.';

        this.loading = false;

        this.cdr.markForCheck();
      }
    });
  }

  applyFilters(): void {

    const search =
      this.searchText.toLowerCase().trim();

    this.filteredRenewals =
      this.renewals.filter(renewal => {

        const matchesSearch =
          !search ||
          this.getContractTitle(
            renewal.contract_id
          ).toLowerCase().includes(search) ||
          String(renewal.contract_id).includes(search);

        const matchesStatus =
          !this.selectedStatus ||
          renewal.renewal_status === this.selectedStatus;

        return matchesSearch && matchesStatus;
      });
  }

  openCreateForm(): void {

    this.editingRenewal = null;

    this.renewalForm.reset();

    this.showForm = true;

    this.errorMessage = '';
    this.successMessage = '';
  }

  openEditForm(renewal: Renewal): void {

    this.editingRenewal = renewal;

    this.renewalForm.patchValue({
      contract_id: renewal.contract_id,
      renewal_date: renewal.renewal_date,
      previous_expiry_date:
        renewal.previous_expiry_date || '',
      new_expiry_date:
        renewal.new_expiry_date || '',
      assigned_to:
        renewal.assigned_to || '',
      notes:
        renewal.notes || ''
    });

    this.showForm = true;

    this.errorMessage = '';
    this.successMessage = '';
  }

  cancelForm(): void {

    this.showForm = false;

    this.editingRenewal = null;

    this.renewalForm.reset();
  }

  saveRenewal(): void {

    if (this.renewalForm.invalid) {

      this.renewalForm.markAllAsTouched();

      return;
    }

    const formValue =
      this.renewalForm.getRawValue();

    if (
      formValue.renewal_date &&
      formValue.new_expiry_date &&
      formValue.new_expiry_date <= formValue.renewal_date
    ) {

      this.errorMessage =
        'New expiry date must be later than renewal date.';

      return;
    }

    this.saving = true;

    this.errorMessage = '';
    this.successMessage = '';

    if (this.editingRenewal) {

      const updateData = {

        renewal_date:
          formValue.renewal_date,

        new_expiry_date:
          formValue.new_expiry_date,

        assigned_to:
          formValue.assigned_to
            ? Number(formValue.assigned_to)
            : undefined,

        notes:
          formValue.notes || undefined
      };

      this.renewalsService.updateRenewal(
        this.editingRenewal.id,
        updateData
      ).subscribe({

        next: () => {

          this.saving = false;

          this.successMessage =
            'Renewal updated successfully.';

          this.showForm = false;

          this.editingRenewal = null;

          this.renewalForm.reset();

          this.loadRenewals();
        },

        error: (error) => {

          console.error(
            'Update renewal error:',
            error
          );

          this.saving = false;

          this.errorMessage =
            error.error?.detail ||
            'Unable to update renewal.';

          this.cdr.markForCheck();
        }
      });

    } else {

      const renewalData: RenewalCreate = {

        contract_id:
          Number(formValue.contract_id),

        renewal_date:
          formValue.renewal_date,

        previous_expiry_date:
          formValue.previous_expiry_date,

        new_expiry_date:
          formValue.new_expiry_date,

        assigned_to:
          formValue.assigned_to
            ? Number(formValue.assigned_to)
            : undefined,

        notes:
          formValue.notes || undefined
      };

      this.renewalsService.createRenewal(
        renewalData
      ).subscribe({

        next: () => {

          this.saving = false;

          this.successMessage =
            'Renewal created successfully.';

          this.showForm = false;

          this.renewalForm.reset();

          this.loadRenewals();
        },

        error: (error) => {

          console.error(
            'Create renewal error:',
            error
          );

          this.saving = false;

          this.errorMessage =
            error.error?.detail ||
            'Unable to create renewal.';

          this.cdr.markForCheck();
        }
      });
    }
  }

  viewRenewal(
    renewal: Renewal
  ): void {

    this.loading = true;

    this.errorMessage = '';

    this.renewalsService.getRenewal(
      renewal.id
    ).subscribe({

      next: (data) => {

        this.selectedRenewal = data;

        this.loading = false;

        this.cdr.markForCheck();
      },

      error: (error) => {

        console.error(
          'Renewal details error:',
          error
        );

        this.errorMessage =
          'Unable to load renewal details.';

        this.loading = false;

        this.cdr.markForCheck();
      }
    });
  }

  closeDetails(): void {
    this.selectedRenewal = null;
  }

  updateStatus(
    renewal: Renewal,
    status: string
  ): void {

    this.renewalsService.updateStatus(
      renewal.id,
      status
    ).subscribe({

      next: () => {

        this.successMessage =
          'Renewal status updated successfully.';

        this.loadRenewals();
      },

      error: (error) => {

        console.error(
          'Renewal status error:',
          error
        );

        this.errorMessage =
          error.error?.detail ||
          'Unable to update renewal status.';

        this.cdr.markForCheck();
      }
    });
  }

  renewContract(
    renewal: Renewal
  ): void {

    this.renewalsService.renewContract(
      renewal.id
    ).subscribe({

      next: () => {

        this.successMessage =
          'Contract renewed successfully.';

        this.loadRenewals();
        this.loadContracts();
      },

      error: (error) => {

        console.error(
          'Renew contract error:',
          error
        );

        this.errorMessage =
          error.error?.detail ||
          'Unable to renew contract.';

        this.cdr.markForCheck();
      }
    });
  }

  getContractTitle(
    contractId: number
  ): string {

    const contract =
      this.contracts.find(
        item => item.id === contractId
      );

    return contract
      ? contract.title
      : `Contract #${contractId}`;
  }
}
