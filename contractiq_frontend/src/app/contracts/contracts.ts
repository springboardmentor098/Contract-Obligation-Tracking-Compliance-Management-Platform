import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
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
  ContractsService,
  Contract,
  ContractCreate
} from '../services/contracts';

@Component({
  selector: 'app-contracts',
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
  templateUrl: './contracts.html',
  styleUrl: './contracts.css'
})
export class Contracts implements OnInit {

  contracts: Contract[] = [];
  filteredContracts: Contract[] = [];

  loading = false;
  saving = false;
  errorMessage = '';
  successMessage = '';

  searchText = '';
  selectedStatus = '';

  showForm = false;
  editingContract: Contract | null = null;
  selectedContract: Contract | null = null;
  displayedColumns = [
    'contract_number',
    'title',
    'category',
    'start_date',
    'end_date',
    'status',
    'actions'
  ];

  contractForm!: FormGroup;

  statuses = [
    'Draft',
    'Under Review',
    'Approved',
    'Active',
    'Expired',
    'Terminated'
  ];

 private formBuilder = inject(FormBuilder);

constructor(
  private contractsService: ContractsService,
  private cdr: ChangeDetectorRef
) {}
  ngOnInit(): void {
  this.contractForm = this.formBuilder.group({
    title: ['', Validators.required],
    contract_number: ['', Validators.required],
    category: ['', Validators.required],
    description: [''],
    start_date: ['', Validators.required],
    end_date: ['', Validators.required]
  });

  this.loadContracts();
}

  loadContracts(): void {
    this.loading = true;
    this.errorMessage = '';

    this.contractsService.getContracts().subscribe({
      next: (data) => {
        this.contracts = data;
        this.applyFilters();
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Contracts API error:', error);
        this.errorMessage = 'Unable to load contracts.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  applyFilters(): void {
    const search = this.searchText.toLowerCase().trim();

    this.filteredContracts = this.contracts.filter(contract => {
      const matchesSearch =
        !search ||
        contract.title.toLowerCase().includes(search) ||
        contract.contract_number.toLowerCase().includes(search) ||
        contract.category.toLowerCase().includes(search);

      const matchesStatus =
        !this.selectedStatus ||
        contract.status === this.selectedStatus;

      return matchesSearch && matchesStatus;
    });
  }

  openCreateForm(): void {
    this.editingContract = null;
    this.contractForm.reset();
    this.showForm = true;
    this.successMessage = '';
    this.errorMessage = '';
  }

  openEditForm(contract: Contract): void {
    this.editingContract = contract;

    this.contractForm.patchValue({
      title: contract.title,
      contract_number: contract.contract_number,
      category: contract.category,
      description: contract.description || '',
      start_date: contract.start_date,
      end_date: contract.end_date
    });

    this.showForm = true;
    this.successMessage = '';
    this.errorMessage = '';
  }
  viewContract(contract: Contract): void {
  this.loading = true;
  this.errorMessage = '';

  this.contractsService.getContract(contract.id).subscribe({
    next: (data) => {
      this.selectedContract = data;
      this.loading = false;
      this.cdr.markForCheck();
    },
    error: (error) => {
      console.error('Contract details error:', error);
      this.errorMessage = 'Unable to load contract details.';
      this.loading = false;
      this.cdr.markForCheck();
    }
  });
}

closeDetails(): void {
  this.selectedContract = null;
}
  cancelForm(): void {
    this.showForm = false;
    this.editingContract = null;
    this.contractForm.reset();
  }

  saveContract(): void {
    if (this.contractForm.invalid) {
      this.contractForm.markAllAsTouched();
      return;
    }

    const formValue = this.contractForm.getRawValue();

    if (
      formValue.start_date &&
      formValue.end_date &&
      formValue.end_date < formValue.start_date
    ) {
      this.errorMessage = 'End date must be later than or equal to start date.';
      return;
    }

    this.saving = true;
    this.errorMessage = '';
    this.successMessage = '';

    if (this.editingContract) {
      const updateData = {
        title: formValue.title!,
        category: formValue.category!,
        description: formValue.description || undefined,
        start_date: formValue.start_date!,
        end_date: formValue.end_date!
      };

      this.contractsService.updateContract(
        this.editingContract.id,
        updateData
      ).subscribe({
        next: () => {
          this.saving = false;
          this.successMessage = 'Contract updated successfully.';
          this.showForm = false;
          this.editingContract = null;
          this.contractForm.reset();
          this.loadContracts();
        },
        error: (error) => {
          console.error('Update contract error:', error);
          this.saving = false;
          this.errorMessage =
            error.status === 409
              ? 'Contract number already exists.'
              : 'Unable to update contract.';
          this.cdr.markForCheck();
        }
      });

    } else {
      const contractData: ContractCreate = {
        title: formValue.title!,
        contract_number: formValue.contract_number!,
        category: formValue.category!,
        description: formValue.description || undefined,
        start_date: formValue.start_date!,
        end_date: formValue.end_date!
      };

      this.contractsService.createContract(contractData).subscribe({
        next: () => {
          this.saving = false;
          this.successMessage = 'Contract created successfully.';
          this.showForm = false;
          this.contractForm.reset();
          this.loadContracts();
        },
        error: (error) => {
          console.error('Create contract error:', error);
          this.saving = false;
          this.errorMessage =
            error.status === 409
              ? 'Contract number already exists.'
              : 'Unable to create contract.';
          this.cdr.markForCheck();
        }
      });
    }
  }

  submitForReview(contract: Contract): void {
    this.contractsService.submitForReview(contract.id).subscribe({
      next: () => {
        this.successMessage = 'Contract submitted for review.';
        this.loadContracts();
      },
      error: (error) => {
        console.error('Submit review error:', error);
        this.errorMessage =
          error.error?.detail || 'Unable to submit contract for review.';
        this.cdr.markForCheck();
      }
    });
  }

  approveContract(contract: Contract): void {
    this.contractsService.approveContract(contract.id).subscribe({
      next: () => {
        this.successMessage = 'Contract approved successfully.';
        this.loadContracts();
      },
      error: (error) => {
        console.error('Approve contract error:', error);
        this.errorMessage =
          error.error?.detail || 'Unable to approve contract.';
        this.cdr.markForCheck();
      }
    });
  }

  activateContract(contract: Contract): void {
    this.contractsService.activateContract(contract.id).subscribe({
      next: () => {
        this.successMessage = 'Contract activated successfully.';
        this.loadContracts();
      },
      error: (error) => {
        console.error('Activate contract error:', error);
        this.errorMessage =
          error.error?.detail || 'Unable to activate contract.';
        this.cdr.markForCheck();
      }
    });
  }

  updateStatus(contract: Contract, status: string): void {
    this.contractsService.updateStatus(
      contract.id,
      status
    ).subscribe({
      next: () => {
        this.successMessage = 'Contract status updated successfully.';
        this.loadContracts();
      },
      error: (error) => {
        console.error('Status update error:', error);
        this.errorMessage =
          error.error?.detail || 'Unable to update contract status.';
        this.cdr.markForCheck();
      }
    });
  }
}
