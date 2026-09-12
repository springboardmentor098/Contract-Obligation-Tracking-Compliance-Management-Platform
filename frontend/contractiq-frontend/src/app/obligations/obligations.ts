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
  Obligation,
  ObligationCreate,
  ObligationService
} from '../services/obligation';

import {
  Contract,
  ContractService
} from '../services/contract';


@Component({
  selector: 'app-obligations',
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

  templateUrl: './obligations.html',
  styleUrl: './obligations.less'
})
export class Obligations implements OnInit {

  // ===============================
  // OBLIGATION DATA
  // ===============================

  obligations: Obligation[] = [];
  filteredObligations: Obligation[] = [];


  // ===============================
  // CONTRACT DATA
  // ===============================

  contracts: Contract[] = [];


  // ===============================
  // FILTERS
  // ===============================

  searchText = '';
  selectedStatus = 'All';


  // ===============================
  // UI STATE
  // ===============================

  loading = false;
  errorMessage = '';

  showCreateForm = false;
  creating = false;
  createError = '';
  createSuccess = '';


  // ===============================
  // CREATE FORM
  // ===============================

  newObligation: ObligationCreate = {
    contract_id: 0,
    title: '',
    description: '',
    obligation_type: 'Reporting Requirement',
    due_date: '',
    assigned_to: 0
  };


  // ===============================
  // OBLIGATION TYPES
  // ===============================

  obligationTypes = [
    'Payment Obligation',
    'Delivery Commitment',
    'Reporting Requirement',
    'Renewal Condition',
    'Service Level Agreement',
    'Legal Compliance Requirement'
  ];


  // ===============================
  // CONSTRUCTOR
  // ===============================

  constructor(
    private obligationService: ObligationService,
    private contractService: ContractService
  ) {}


  // ===============================
  // INITIALIZATION
  // ===============================

  ngOnInit(): void {

    this.loadObligations();
    this.loadContracts();

  }


  // ===============================
  // LOAD OBLIGATIONS
  // ===============================

  loadObligations(): void {

    this.loading = true;
    this.errorMessage = '';

    this.obligationService.getObligations().subscribe({

      next: (data) => {

        console.log(
          'Obligations API data:',
          data
        );

        this.obligations = data;
        this.filteredObligations = data;

        this.loading = false;

      },

      error: (error) => {

        console.error(
          'Failed to load obligations:',
          error
        );

        this.loading = false;

        this.errorMessage =
          'Unable to load obligations. Please try again.';

      }

    });
  }


  // ===============================
  // LOAD CONTRACTS
  // ===============================

  loadContracts(): void {

    this.contractService.getContracts().subscribe({

      next: (data) => {

        console.log(
          'Contracts for obligation form:',
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


  // ===============================
  // SEARCH + STATUS FILTER
  // ===============================

  applyFilters(): void {

    const search =
      this.searchText
        .trim()
        .toLowerCase();

    this.filteredObligations =
      this.obligations.filter((obligation) => {

        const title =
          obligation.title
            ?.toLowerCase() ?? '';

        const type =
          obligation.obligation_type
            ?.toLowerCase() ?? '';

        const status =
          obligation.status
            ?.toLowerCase() ?? '';

        const matchesSearch =
          !search ||
          title.includes(search) ||
          type.includes(search) ||
          status.includes(search);

        const matchesStatus =
          this.selectedStatus === 'All' ||
          obligation.status === this.selectedStatus;

        return (
          matchesSearch &&
          matchesStatus
        );

      });
  }


  // ===============================
  // CLEAR FILTERS
  // ===============================

  clearFilters(): void {

    this.searchText = '';
    this.selectedStatus = 'All';

    this.applyFilters();

  }


  // ===============================
  // OPEN CREATE FORM
  // ===============================

  openCreateForm(): void {

    this.showCreateForm = true;

    this.createError = '';
    this.createSuccess = '';

    this.resetCreateForm();

  }


  // ===============================
  // CLOSE CREATE FORM
  // ===============================

  closeCreateForm(): void {

    this.showCreateForm = false;

    this.createError = '';
    this.createSuccess = '';

    this.resetCreateForm();

  }


  // ===============================
  // RESET CREATE FORM
  // ===============================

  resetCreateForm(): void {

    this.newObligation = {
      contract_id: 0,
      title: '',
      description: '',
      obligation_type: 'Reporting Requirement',
      due_date: '',
      assigned_to: 0
    };

  }


  // ===============================
  // CREATE OBLIGATION
  // ===============================

  createObligation(): void {

    this.createError = '';
    this.createSuccess = '';

    // Basic validation

    if (
      !this.newObligation.contract_id ||
      !this.newObligation.title.trim() ||
      !this.newObligation.obligation_type ||
      !this.newObligation.due_date ||
      !this.newObligation.assigned_to
    ) {

      this.createError =
        'Please fill in all required fields.';

      return;
    }


    this.creating = true;


    const data: ObligationCreate = {

      contract_id:
        Number(this.newObligation.contract_id),

      title:
        this.newObligation.title.trim(),

      description:
        this.newObligation.description?.trim() || null,

      obligation_type:
        this.newObligation.obligation_type,

      due_date:
        this.newObligation.due_date,

      assigned_to:
        Number(this.newObligation.assigned_to)

    };


    this.obligationService
      .createObligation(data)
      .subscribe({

        next: (response) => {

          console.log(
            'Obligation created:',
            response
          );

          this.creating = false;

          this.createSuccess =
            'Obligation created successfully.';

          // Refresh table with real backend data
          this.loadObligations();

          // Close form after successful creation
          setTimeout(() => {

            this.showCreateForm = false;
            this.createSuccess = '';
            this.resetCreateForm();

          }, 800);

        },


        error: (error) => {

          console.error(
            'Failed to create obligation:',
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
              'You are not authorized to create this obligation.';

          }
          else if (error.status === 422) {

            this.createError =
              'Please check the entered information.';

          }
          else {

            this.createError =
              error.error?.detail ||
              'Unable to create obligation. Please try again.';

          }

        }

      });

  }


  // ===============================
  // STATUS CSS CLASS
  // ===============================

  getStatusClass(status: string): string {

    return status
      .toLowerCase()
      .replace(/\s+/g, '-');

  }


  // ===============================
  // CHECK OVERDUE
  // ===============================

  isOverdue(
    obligation: Obligation
  ): boolean {

    if (
      obligation.status === 'Completed' ||
      !obligation.due_date
    ) {

      return false;
    }

    const today = new Date();

    const dueDate =
      new Date(obligation.due_date);

    today.setHours(0, 0, 0, 0);
    dueDate.setHours(0, 0, 0, 0);

    return dueDate < today;
  }

}