import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';

import {
  Renewal,
  RenewalCreate,
  RenewalService
} from '../services/renewal';

import {
  Contract,
  ContractService
} from '../services/contract';

@Component({
  selector: 'app-renewals',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule
  ],
  templateUrl: './renewals.html',
  styleUrl: './renewals.less'
})
export class Renewals implements OnInit {

  renewals: Renewal[] = [];
  filteredRenewals: Renewal[] = [];

  contracts: Contract[] = [];

  searchText = '';
  selectedStatus = 'All';

  loading = false;
  errorMessage = '';

  showCreateForm = false;
  creating = false;

  createError = '';
  createSuccess = '';

  renewingId: number | null = null;
  renewError = '';

  newRenewal: RenewalCreate = {
    contract_id: 0,
    renewal_date: '',
    previous_expiry_date: '',
    new_expiry_date: '',
    assigned_to: 0,
    notes: ''
  };

  renewalStatuses = [
    'Upcoming',
    'In Progress',
    'Renewed',
    'Expired',
    'Cancelled'
  ];

  constructor(
    private renewalService: RenewalService,
    private contractService: ContractService
  ) {}

  ngOnInit(): void {
    this.loadRenewals();
    this.loadContracts();
  }

  // =========================================
  // LOAD RENEWALS
  // =========================================

  loadRenewals(): void {
    this.loading = true;
    this.errorMessage = '';

    this.renewalService.getRenewals().subscribe({
      next: (data) => {
        console.log('Renewals API data:', data);

        this.renewals = data;
        this.applyFilters();

        this.loading = false;
      },

      error: (error) => {
        console.error(
          'Failed to load renewals:',
          error
        );

        this.loading = false;

        this.errorMessage =
          'Unable to load renewals. Please try again.';
      }
    });
  }

  // =========================================
  // LOAD CONTRACTS
  // =========================================

  loadContracts(): void {
    this.contractService.getContracts().subscribe({
      next: (data) => {
        console.log(
          'Contracts for renewal form:',
          data
        );

        this.contracts = data;
      },

      error: (error) => {
        console.error(
          'Failed to load contracts:',
          error
        );
      }
    });
  }

  // =========================================
  // FILTERS
  // =========================================

  applyFilters(): void {
    const search =
      this.searchText
        .trim()
        .toLowerCase();

    this.filteredRenewals =
      this.renewals.filter((renewal) => {

        const contractId =
          String(renewal.contract_id);

        const status =
          renewal.status
            ?.toLowerCase() ?? '';

        const notes =
          renewal.notes
            ?.toLowerCase() ?? '';

        const matchesSearch =
          !search ||
          contractId.includes(search) ||
          status.includes(search) ||
          notes.includes(search);

        const matchesStatus =
          this.selectedStatus === 'All' ||
          renewal.status === this.selectedStatus;

        return (
          matchesSearch &&
          matchesStatus
        );
      });
  }

  clearFilters(): void {
    this.searchText = '';
    this.selectedStatus = 'All';

    this.applyFilters();
  }

  // =========================================
  // CREATE FORM
  // =========================================

  openCreateForm(): void {
    this.showCreateForm = true;

    this.createError = '';
    this.createSuccess = '';

    this.resetCreateForm();
  }

  closeCreateForm(): void {
    this.showCreateForm = false;

    this.createError = '';
    this.createSuccess = '';

    this.resetCreateForm();
  }

  resetCreateForm(): void {
    this.newRenewal = {
      contract_id: 0,
      renewal_date: '',
      previous_expiry_date: '',
      new_expiry_date: '',
      assigned_to: 0,
      notes: ''
    };
  }

  // =========================================
  // CREATE RENEWAL
  // =========================================

  createRenewal(): void {
    this.createError = '';
    this.createSuccess = '';

    if (
      !this.newRenewal.contract_id ||
      !this.newRenewal.renewal_date ||
      !this.newRenewal.previous_expiry_date ||
      !this.newRenewal.new_expiry_date ||
      !this.newRenewal.assigned_to
    ) {
      this.createError =
        'Please fill in all required fields.';

      return;
    }

    this.creating = true;

    const data: RenewalCreate = {
      contract_id:
        Number(this.newRenewal.contract_id),

      renewal_date:
        this.newRenewal.renewal_date,

      previous_expiry_date:
        this.newRenewal.previous_expiry_date,

      new_expiry_date:
        this.newRenewal.new_expiry_date,

      assigned_to:
        Number(this.newRenewal.assigned_to),

      notes:
        this.newRenewal.notes?.trim() || null
    };

    this.renewalService
      .createRenewal(data)
      .subscribe({

        next: (response) => {
          console.log(
            'Renewal created:',
            response
          );

          this.creating = false;

          this.createSuccess =
            'Renewal created successfully.';

          this.loadRenewals();

          setTimeout(() => {
            this.showCreateForm = false;

            this.createSuccess = '';

            this.resetCreateForm();
          }, 800);
        },

        error: (error) => {
          console.error(
            'Failed to create renewal:',
            error
          );

          this.creating = false;

          if (error.status === 404) {
            this.createError =
              error.error?.detail ||
              'Contract or assigned user not found.';
          }

          else if (error.status === 401) {
            this.createError =
              'Your session has expired. Please login again.';
          }

          else if (error.status === 403) {
            this.createError =
              'You are not authorized to create this renewal.';
          }

          else if (error.status === 422) {
            this.createError =
              'Please check the entered information.';
          }

          else {
            this.createError =
              error.error?.detail ||
              'Unable to create renewal. Please try again.';
          }
        }
      });
  }

  // =========================================
  // RENEW CONTRACT
  // =========================================

  renewContract(
    renewal: Renewal
  ): void {

    if (
      renewal.status === 'Renewed' ||
      renewal.status === 'Cancelled'
    ) {
      return;
    }

    this.renewingId = renewal.id;
    this.renewError = '';

    this.renewalService
      .renewContract(renewal.id)
      .subscribe({

        next: (response) => {
          console.log(
            'Contract renewed:',
            response
          );

          this.renewingId = null;

          this.loadRenewals();
        },

        error: (error) => {
          console.error(
            'Failed to renew contract:',
            error
          );

          this.renewingId = null;

          if (error.status === 401) {
            this.renewError =
              'Your session has expired. Please login again.';
          }

          else if (error.status === 403) {
            this.renewError =
              'You are not authorized to renew this contract.';
          }

          else {
            this.renewError =
              error.error?.detail ||
              'Unable to renew contract. Please try again.';
          }
        }
      });
  }

  // =========================================
  // STATUS CLASS
  // =========================================

  getStatusClass(
    status: string
  ): string {

    return status
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  // =========================================
  // DATE HELPERS
  // =========================================

  isExpired(
    renewal: Renewal
  ): boolean {

    if (
      renewal.status === 'Renewed' ||
      !renewal.new_expiry_date
    ) {
      return false;
    }

    const today = new Date();

    const expiryDate =
      new Date(
        renewal.new_expiry_date
      );

    today.setHours(0, 0, 0, 0);
    expiryDate.setHours(0, 0, 0, 0);

    return expiryDate < today;
  }
}