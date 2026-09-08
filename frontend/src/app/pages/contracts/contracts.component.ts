import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
  Contract,
  ContractCreate,
  ContractService
} from '../../services/contract.service';

import {
  AuthService,
  UserRole
} from '../../services/auth.service';

@Component({
  selector: 'app-contracts',
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
    MatTableModule,
    MatTooltipModule
  ],
  templateUrl: './contracts.component.html',
  styleUrl: './contracts.component.scss'
})
export class ContractsComponent implements OnInit {

  private readonly contractService = inject(ContractService);
  private readonly authService = inject(AuthService);

  contracts: Contract[] = [];
  filteredContracts: Contract[] = [];

  loading = true;
  error = '';

  searchTerm = '';

  showCreateForm = false;
  creating = false;
  createError = '';

  contractForm: ContractCreate = {
    title: '',
    contract_number: '',
    category: '',
    description: '',
    counterparty_name: '',
    start_date: null,
    end_date: null,
    contract_value: null,
    currency: 'INR',
    assigned_to: null
  };

  displayedColumns: string[] = [
    'contract_number',
    'title',
    'category',
    'counterparty_name',
    'start_date',
    'end_date',
    'status',
    'actions'
  ];

  readonly UserRole = UserRole;

  ngOnInit(): void {
    this.loadContracts();
  }

  loadContracts(): void {
    this.loading = true;
    this.error = '';

    this.contractService.getContracts().subscribe({
      next: (contracts) => {
        this.contracts = contracts;
        this.filteredContracts = [...contracts];
        this.loading = false;
      },

      error: (error) => {
        console.error('Contracts API error:', error);

        this.loading = false;

        if (error.status === 401) {
          this.error =
            'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.error =
            'You do not have permission to view these contracts.';
        } else if (error.status === 0) {
          this.error =
            'Unable to connect to the backend. Please make sure FastAPI is running.';
        } else {
          this.error =
            error.error?.detail ||
            'Unable to load contracts. Please try again.';
        }
      }
    });
  }

  onSearch(): void {
    const search = this.searchTerm.trim().toLowerCase();

    if (!search) {
      this.filteredContracts = [...this.contracts];
      return;
    }

    this.filteredContracts = this.contracts.filter((contract) =>
      [
        contract.contract_number,
        contract.title,
        contract.category,
        contract.counterparty_name,
        contract.status
      ]
        .filter(Boolean)
        .some((value) =>
          String(value).toLowerCase().includes(search)
        )
    );
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.filteredContracts = [...this.contracts];
  }

  hasAnyRole(roles: UserRole[]): boolean {
    return this.authService.hasAnyRole(roles);
  }

  canDelete(): boolean {
    return this.authService.hasRole(
      UserRole.ADMINISTRATOR
    );
  }

  canManageContracts(): boolean {
    return this.hasAnyRole([
      UserRole.ADMINISTRATOR,
      UserRole.LEGAL_MANAGER,
      UserRole.CONTRACT_MANAGER
    ]);
  }

  canApprove(): boolean {
    return this.hasAnyRole([
      UserRole.ADMINISTRATOR,
      UserRole.LEGAL_MANAGER
    ]);
  }

  canSubmitForReview(contract: Contract): boolean {
    return (
      this.canManageContracts() &&
      contract.status === 'Draft'
    );
  }

  canApproveContract(contract: Contract): boolean {
    return (
      this.canApprove() &&
      contract.status === 'Under Review'
    );
  }

  canActivateContract(contract: Contract): boolean {
    return (
      this.canManageContracts() &&
      contract.status === 'Approved'
    );
  }

  openCreateForm(): void {
    this.createError = '';

    this.contractForm = {
      title: '',
      contract_number: '',
      category: '',
      description: '',
      counterparty_name: '',
      start_date: null,
      end_date: null,
      contract_value: null,
      currency: 'INR',
      assigned_to: null
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

  createContract(): void {
    this.createError = '';

    if (!this.contractForm.title.trim()) {
      this.createError = 'Contract title is required.';
      return;
    }

    if (!this.contractForm.contract_number.trim()) {
      this.createError = 'Contract number is required.';
      return;
    }

    if (!this.contractForm.category.trim()) {
      this.createError = 'Contract category is required.';
      return;
    }

    if (
      this.contractForm.start_date &&
      this.contractForm.end_date &&
      this.contractForm.start_date > this.contractForm.end_date
    ) {
      this.createError =
        'End date must be after the start date.';
      return;
    }

    this.creating = true;

    const contract: ContractCreate = {
      ...this.contractForm,
      title: this.contractForm.title.trim(),
      contract_number:
        this.contractForm.contract_number.trim(),
      category: this.contractForm.category.trim(),
      description:
        this.contractForm.description?.trim() || null,
      counterparty_name:
        this.contractForm.counterparty_name?.trim() || null,
      contract_value:
        this.contractForm.contract_value === null ||
        this.contractForm.contract_value === undefined ||
        Number.isNaN(this.contractForm.contract_value)
          ? null
          : Number(this.contractForm.contract_value),
      currency:
        this.contractForm.currency?.trim().toUpperCase() || null,
      assigned_to:
        this.contractForm.assigned_to || null
    };

    this.contractService.createContract(contract).subscribe({
      next: () => {
        this.creating = false;
        this.showCreateForm = false;
        this.createError = '';

        this.loadContracts();
      },

      error: (error) => {
        console.error('Create contract error:', error);

        this.creating = false;

        if (error.status === 400) {
          this.createError =
            error.error?.detail ||
            'Invalid contract information.';
        } else if (error.status === 401) {
          this.createError =
            'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.createError =
            'You do not have permission to create contracts.';
        } else if (error.status === 0) {
          this.createError =
            'Unable to connect to the backend.';
        } else {
          this.createError =
            error.error?.detail ||
            'Unable to create contract. Please try again.';
        }
      }
    });
  }

  submitForReview(contract: Contract): void {
    this.contractService
      .submitForReview(contract.id)
      .subscribe({
        next: () => {
          this.loadContracts();
        },

        error: (error) => {
          console.error(
            'Submit review error:',
            error
          );

          this.error =
            error.error?.detail ||
            'Unable to submit contract for review.';
        }
      });
  }

  approveContract(contract: Contract): void {
    this.contractService
      .approveContract(contract.id)
      .subscribe({
        next: () => {
          this.loadContracts();
        },

        error: (error) => {
          console.error(
            'Approve contract error:',
            error
          );

          this.error =
            error.error?.detail ||
            'Unable to approve contract.';
        }
      });
  }

  activateContract(contract: Contract): void {
    this.contractService
      .activateContract(contract.id)
      .subscribe({
        next: () => {
          this.loadContracts();
        },

        error: (error) => {
          console.error(
            'Activate contract error:',
            error
          );

          this.error =
            error.error?.detail ||
            'Unable to activate contract.';
        }
      });
  }

  deleteContract(contract: Contract): void {
    const confirmed = window.confirm(
      `Are you sure you want to delete contract "${contract.title}"?`
    );

    if (!confirmed) {
      return;
    }

    this.contractService
      .deleteContract(contract.id)
      .subscribe({
        next: () => {
          this.loadContracts();
        },

        error: (error) => {
          console.error(
            'Delete contract error:',
            error
          );

          this.error =
            error.error?.detail ||
            'Unable to delete contract.';
        }
      });
  }

  formatValue(contract: Contract): string {
    if (
      contract.contract_value === null ||
      contract.contract_value === undefined
    ) {
      return '—';
    }

    const currency = contract.currency
      ? `${contract.currency} `
      : '';

    return `${currency}${contract.contract_value}`;
  }

  getStatusClass(status: string): string {
    return status
      .toLowerCase()
      .replace(/\s+/g, '-');
  }
}