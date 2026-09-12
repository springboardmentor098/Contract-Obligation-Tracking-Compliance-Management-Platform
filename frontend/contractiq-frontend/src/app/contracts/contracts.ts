import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';

import {
  Contract,
  ContractService,
  CreateContract,
  UpdateContract
} from '../services/contract';

@Component({
  selector: 'app-contracts',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatTableModule
  ],
  templateUrl: './contracts.html',
  styleUrl: './contracts.less'
})
export class Contracts implements OnInit {

  // =========================================================
  // CONTRACT DATA
  // =========================================================

  contracts: Contract[] = [];
  filteredContracts: Contract[] = [];

  loading = false;
  errorMessage = '';
  isEmpty = false;


  // =========================================================
  // SEARCH / FILTER
  // =========================================================

  searchTerm = '';
  selectedCategory = '';
  selectedStatus = '';

  categories: string[] = [
    'Employment Contract',
    'Vendor Contract',
    'Service Agreement',
    'NDA',
    'Lease Agreement',
    'Partnership Agreement',
    'Other'
  ];

  statuses: string[] = [
    'Draft',
    'Under Review',
    'Approved',
    'Active',
    'Expired',
    'Terminated'
  ];


  // =========================================================
  // CREATE CONTRACT
  // =========================================================

  showCreateForm = false;
  creating = false;

  createError = '';
  createSuccess = '';

  // Top success popup
  createSuccessPopup = false;

  createContractData: CreateContract = {
    contract_number: '',
    title: '',
    category: '',
    description: '',
    party_name: '',
    start_date: '',
    end_date: ''
  };


  // =========================================================
  // EDIT CONTRACT
  // =========================================================

  showEditForm = false;
  editing = false;

  editingContractId: number | null = null;

  editError = '';
  editSuccess = '';

  editContractData: UpdateContract = {
    title: '',
    category: '',
    description: '',
    party_name: '',
    start_date: '',
    end_date: ''
  };


  // =========================================================
  // VIEW CONTRACT
  // =========================================================

  showViewModal = false;
  selectedContract: Contract | null = null;

  viewLoading = false;
  viewError = '';


  // =========================================================
  // CONSTRUCTOR
  // =========================================================

  constructor(
    private contractService: ContractService
  ) {}


  // =========================================================
  // INIT
  // =========================================================

  ngOnInit(): void {
    this.loadContracts();
  }


  // =========================================================
  // LOAD CONTRACTS
  // =========================================================

  loadContracts(): void {

    this.loading = true;
    this.errorMessage = '';

    this.contractService.getContracts().subscribe({

      next: (data) => {

        this.contracts = data || [];

        this.filteredContracts = [
          ...this.contracts
        ];

        this.isEmpty =
          this.contracts.length === 0;

        this.loading = false;

        this.applyFilters();
      },

      error: (error) => {

        console.error(
          'Error loading contracts:',
          error
        );

        this.loading = false;

        this.isEmpty = false;

        if (error.status === 401) {

          this.errorMessage =
            'Your session has expired. Please login again.';

        } else if (error.status === 403) {

          this.errorMessage =
            'You are not authorized to view contracts.';

        } else {

          this.errorMessage =
            'Unable to load contracts. Please check the backend connection.';
        }
      }
    });
  }


  // =========================================================
  // SEARCH
  // =========================================================

  onSearch(): void {
    this.applyFilters();
  }


  // =========================================================
  // FILTER
  // =========================================================

  applyFilters(): void {

    const search =
      this.searchTerm
        .trim()
        .toLowerCase();

    this.filteredContracts =
      this.contracts.filter(
        (contract) => {

          const matchesSearch =
            !search ||
            contract.contract_number
              ?.toLowerCase()
              .includes(search) ||
            contract.title
              ?.toLowerCase()
              .includes(search) ||
            contract.party_name
              ?.toLowerCase()
              .includes(search) ||
            contract.category
              ?.toLowerCase()
              .includes(search);

          const matchesCategory =
            !this.selectedCategory ||
            contract.category ===
              this.selectedCategory;

          const matchesStatus =
            !this.selectedStatus ||
            contract.status ===
              this.selectedStatus;

          return (
            matchesSearch &&
            matchesCategory &&
            matchesStatus
          );
        }
      );
  }


  // =========================================================
  // CLEAR FILTERS
  // =========================================================

  clearFilters(): void {

    this.searchTerm = '';
    this.selectedCategory = '';
    this.selectedStatus = '';

    this.applyFilters();
  }


  // =========================================================
  // CREATE FORM
  // =========================================================

  openCreateForm(): void {

    this.showCreateForm = true;

    // Close edit form
    this.showEditForm = false;

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

    this.createContractData = {

      contract_number: '',
      title: '',
      category: '',
      description: '',
      party_name: '',
      start_date: '',
      end_date: ''

    };
  }


  // =========================================================
  // CREATE CONTRACT
  // =========================================================

  createContract(): void {

    this.createError = '';
    this.createSuccess = '';

    // -----------------------------------------
    // VALIDATION
    // -----------------------------------------

    if (
      !this.createContractData.contract_number.trim() ||
      !this.createContractData.title.trim() ||
      !this.createContractData.category ||
      !this.createContractData.party_name.trim() ||
      !this.createContractData.start_date ||
      !this.createContractData.end_date
    ) {

      this.createError =
        'Please fill all required fields.';

      return;
    }


    // -----------------------------------------
    // DATE VALIDATION
    // -----------------------------------------

    if (
      this.createContractData.end_date <
      this.createContractData.start_date
    ) {

      this.createError =
        'End date cannot be before start date.';

      return;
    }


    // -----------------------------------------
    // START CREATING
    // -----------------------------------------

    this.creating = true;


    this.contractService
      .createContract(
        this.createContractData
      )
      .subscribe({

        // ---------------------------------------
        // SUCCESS
        // ---------------------------------------

        next: (response) => {

          console.log(
            'Contract created successfully:',
            response
          );


          this.creating = false;


          // Success message
          this.createSuccess =
            'Contract created successfully.';


          // -------------------------------------
          // SHOW TOP SUCCESS POPUP
          // -------------------------------------

          this.createSuccessPopup = true;


          // -------------------------------------
          // CLOSE CREATE FORM
          // -------------------------------------

          this.showCreateForm = false;


          // -------------------------------------
          // RESET FORM
          // -------------------------------------

          this.resetCreateForm();


          // -------------------------------------
          // RELOAD CONTRACT LIST
          // -------------------------------------

          this.loadContracts();


          // -------------------------------------
          // HIDE POPUP AFTER 3 SECONDS
          // -------------------------------------

          setTimeout(() => {

            this.createSuccessPopup = false;

            this.createSuccess = '';

          }, 3000);
        },


        // ---------------------------------------
        // ERROR
        // ---------------------------------------

        error: (error) => {

          console.error(
            'Error creating contract:',
            error
          );


          this.creating = false;


          if (error.status === 401) {

            this.createError =
              'Session expired. Please login again.';

          } else if (error.status === 403) {

            this.createError =
              'You are not authorized to create contracts.';

          } else if (error.status === 400) {

            this.createError =
              error.error?.detail ||
              'Invalid contract details.';

          } else if (error.status === 409) {

            this.createError =
              'Contract number already exists.';

          } else {

            this.createError =
              'Unable to create contract. Please try again.';
          }
        }
      });
  }


  // =========================================================
  // VIEW CONTRACT
  // =========================================================

  viewContract(
    contractId: number
  ): void {

    this.showViewModal = true;

    this.viewLoading = true;

    this.viewError = '';

    this.selectedContract = null;


    this.contractService
      .getContract(contractId)
      .subscribe({

        next: (contract) => {

          this.selectedContract =
            contract;

          this.viewLoading = false;
        },

        error: (error) => {

          console.error(
            'Error loading contract:',
            error
          );

          this.viewLoading = false;


          if (error.status === 401) {

            this.viewError =
              'Session expired. Please login again.';

          } else if (error.status === 403) {

            this.viewError =
              'You are not authorized to view this contract.';

          } else if (error.status === 404) {

            this.viewError =
              'Contract not found.';

          } else {

            this.viewError =
              'Unable to load contract details.';
          }
        }
      });
  }


  // =========================================================
  // CLOSE VIEW MODAL
  // =========================================================

  closeViewModal(): void {

    this.showViewModal = false;

    this.selectedContract = null;

    this.viewError = '';
  }


  // =========================================================
  // EDIT CONTRACT
  // =========================================================

  editContract(
    contractId: number
  ): void {

    // Close create form
    this.showCreateForm = false;

    // Open edit form
    this.showEditForm = true;

    this.editing = true;

    this.editingContractId =
      contractId;

    this.editError = '';
    this.editSuccess = '';


    this.contractService
      .getContract(contractId)
      .subscribe({

        next: (contract) => {

          this.editContractData = {

            title:
              contract.title || '',

            category:
              contract.category || '',

            description:
              contract.description || '',

            party_name:
              contract.party_name || '',

            start_date:
              this.formatDate(
                contract.start_date
              ),

            end_date:
              this.formatDate(
                contract.end_date
              )
          };


          this.editing = false;
        },


        error: (error) => {

          console.error(
            'Error loading contract for edit:',
            error
          );


          this.editing = false;


          if (error.status === 401) {

            this.editError =
              'Session expired. Please login again.';

          } else if (error.status === 403) {

            this.editError =
              'You are not authorized to edit this contract.';

          } else if (error.status === 404) {

            this.editError =
              'Contract not found.';

          } else {

            this.editError =
              'Unable to load contract details for editing.';
          }
        }
      });
  }


  // =========================================================
  // UPDATE CONTRACT
  // =========================================================

  updateContract(): void {

    this.editError = '';
    this.editSuccess = '';


    // -----------------------------------------
    // CHECK CONTRACT ID
    // -----------------------------------------

    if (!this.editingContractId) {

      this.editError =
        'Invalid contract selected.';

      return;
    }


    // -----------------------------------------
    // VALIDATION
    // -----------------------------------------

    if (
      !this.editContractData.title.trim() ||
      !this.editContractData.category ||
      !this.editContractData.party_name.trim() ||
      !this.editContractData.start_date ||
      !this.editContractData.end_date
    ) {

      this.editError =
        'Please fill all required fields.';

      return;
    }


    // -----------------------------------------
    // DATE VALIDATION
    // -----------------------------------------

    if (
      this.editContractData.end_date <
      this.editContractData.start_date
    ) {

      this.editError =
        'End date cannot be before start date.';

      return;
    }


    this.editing = true;


    this.contractService
      .updateContract(
        this.editingContractId,
        this.editContractData
      )
      .subscribe({

        // ---------------------------------------
        // SUCCESS
        // ---------------------------------------

        next: (updatedContract) => {

          console.log(
            'Contract updated successfully:',
            updatedContract
          );


          this.editing = false;


          this.editSuccess =
            'Contract updated successfully.';


          // -------------------------------------
          // UPDATE LOCAL CONTRACT LIST
          // -------------------------------------

          const index =
            this.contracts.findIndex(
              contract =>
                contract.id ===
                updatedContract.id
            );


          if (index !== -1) {

            this.contracts[index] =
              updatedContract;
          }


          // Apply current filters
          this.applyFilters();


          // -------------------------------------
          // CLOSE EDIT FORM
          // -------------------------------------

          setTimeout(() => {

            this.showEditForm = false;

            this.editSuccess = '';

            this.editingContractId =
              null;

            this.resetEditForm();

          }, 1200);
        },


        // ---------------------------------------
        // ERROR
        // ---------------------------------------

        error: (error) => {

          console.error(
            'Error updating contract:',
            error
          );


          this.editing = false;


          if (error.status === 401) {

            this.editError =
              'Session expired. Please login again.';

          } else if (error.status === 403) {

            this.editError =
              'You are not authorized to update this contract.';

          } else if (error.status === 404) {

            this.editError =
              'Contract not found.';

          } else if (error.status === 400) {

            this.editError =
              error.error?.detail ||
              'Invalid contract details.';

          } else {

            this.editError =
              'Unable to update contract. Please try again.';
          }
        }
      });
  }


  // =========================================================
  // CLOSE EDIT FORM
  // =========================================================

  closeEditForm(): void {

    this.showEditForm = false;

    this.editingContractId = null;

    this.editError = '';
    this.editSuccess = '';

    this.resetEditForm();
  }


  // =========================================================
  // RESET EDIT FORM
  // =========================================================

  resetEditForm(): void {

    this.editContractData = {

      title: '',
      category: '',
      description: '',
      party_name: '',
      start_date: '',
      end_date: ''

    };
  }


  // =========================================================
  // DATE FORMAT
  // =========================================================

  private formatDate(
    date: string | null
  ): string {

    if (!date) {
      return '';
    }

    return date.substring(0, 10);
  }


  // =========================================================
  // STATUS CSS
  // =========================================================

  getStatusClass(status: string): string {
  switch (status) {
    case 'Active':
      return 'active';

    case 'Draft':
      return 'draft';

    case 'Under Review':
      return 'under-review';

    case 'Approved':
      return 'approved';

    case 'Expired':
      return 'expired';

    case 'Terminated':
      return 'terminated';

    default:
      return 'default';
  }
}

}