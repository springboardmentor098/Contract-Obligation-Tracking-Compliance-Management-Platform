import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

import {
  RenewalService,
  RenewalCreatePayload,
  RenewalUpdatePayload
} from '../../core/services/renewal.service';

import { ContractService } from '../../core/services/contract.service';

import {
  Renewal,
  Contract
} from '../../core/models/models';

import { PageHeaderComponent } from '../../shared/page-header.component';
import { StatusComponent } from '../../shared/status.component';
import { EmptyStateComponent } from '../../shared/empty-state.component';


@Component({
  selector: 'cq-renewals',

  standalone: true,

  imports: [
    FormsModule,
    DatePipe,
    PageHeaderComponent,
    StatusComponent,
    EmptyStateComponent
  ],

  templateUrl: './renewals.component.html',

  styleUrl: './renewals.component.css'
})
export class RenewalsComponent {

  private readonly service =
    inject(RenewalService);

  private readonly contractService =
    inject(ContractService);


  // ============================================================
  // DATA
  // ============================================================

  items: Renewal[] = [];

  filtered: Renewal[] = [];

  contracts: Contract[] = [];

  contractsLoading = false;


  // ============================================================
  // EDITING
  // ============================================================

  editing?: Renewal;


  // ============================================================
  // SEARCH / FILTER
  // ============================================================

  query = '';

  status = '';

  statuses = [
    'Upcoming',
    'In Progress',
    'Renewed',
    'Expired',
    'Cancelled'
  ];


  // ============================================================
  // UI STATE
  // ============================================================

  loading = true;

  saving = false;

  error = '';

  showForm = false;


  // ============================================================
  // FORM
  // ============================================================

  form = {

    contract_number: '',

    contract_id: '',

    renewal_date: '',

    previous_expiry_date: '',

    new_expiry_date: '',

    assigned_to: '',

    notes: ''

  };


  // ============================================================
  // CONSTRUCTOR
  // ============================================================

  constructor() {

    this.load();

    this.loadContracts();

  }


  // ============================================================
  // LOAD RENEWALS
  // ============================================================

  load(): void {

    this.loading = true;

    this.error = '';

    this.service.list().subscribe({

      next: (data) => {

        this.items = data ?? [];

        this.apply();

        this.loading = false;

      },

      error: (e) => {

        console.error(
          'Renewal load error:',
          e
        );

        this.error =
          this.getErrorMessage(
            e,
            'Unable to load renewals.'
          );

        this.loading = false;

      }

    });

  }


  // ============================================================
  // LOAD CONTRACTS
  // ============================================================

  loadContracts(): void {

    this.contractsLoading = true;

    this.contractService.list().subscribe({

      next: (data) => {

        this.contracts = data ?? [];

        this.contractsLoading = false;

      },

      error: (e) => {

        console.error(
          'Contract loading error:',
          e
        );

        this.contracts = [];

        this.contractsLoading = false;

      }

    });

  }


  // ============================================================
  // SEARCH / FILTER
  // ============================================================

  apply(): void {

    const q =
      this.query
        .trim()
        .toLowerCase();


    this.filtered =
      this.items.filter(x => {

        const contractNumber =
          this.getContractNumber(
            x.contract_id
          ).toLowerCase();


        const matchesSearch =
          !q ||
          String(x.contract_id)
            .toLowerCase()
            .includes(q) ||
          contractNumber.includes(q);


        const matchesStatus =
          !this.status ||
          x.status === this.status;


        return (
          matchesSearch &&
          matchesStatus
        );

      });

  }


  // ============================================================
  // OPEN CREATE FORM
  // ============================================================

  openForm(): void {

    this.editing = undefined;

    this.error = '';

    this.saving = false;

    this.resetForm();

    this.showForm = true;

  }


  // ============================================================
  // OPEN EDIT FORM
  // ============================================================

  editRenewal(
    renewal: Renewal
  ): void {

    this.editing = renewal;

    this.error = '';

    this.saving = false;


    const contract =
      this.contracts.find(
        c =>
          String(c.id) ===
          String(renewal.contract_id)
      );


    this.form = {

      contract_number:
        contract?.contract_number ?? '',

      contract_id:
        String(renewal.contract_id),

      renewal_date:
        this.formatDate(
          renewal.renewal_date
        ),

      previous_expiry_date:
        this.formatDate(
          renewal.previous_expiry_date
        ),

      new_expiry_date:
        this.formatDate(
          renewal.new_expiry_date
        ),

      assigned_to:
        renewal.assigned_to != null
          ? String(renewal.assigned_to)
          : '',

      notes:
        renewal.notes ?? ''

    };


    this.showForm = true;

  }


  // ============================================================
  // CLOSE FORM
  // ============================================================

  closeForm(): void {

    if (this.saving) {

      return;

    }

    this.showForm = false;

    this.editing = undefined;

    this.saving = false;

    this.error = '';

    this.resetForm();

  }


  // ============================================================
  // RESET FORM
  // ============================================================

  resetForm(): void {

    this.form = {

      contract_number: '',

      contract_id: '',

      renewal_date: '',

      previous_expiry_date: '',

      new_expiry_date: '',

      assigned_to: '',

      notes: ''

    };

  }


  // ============================================================
  // CONTRACT SELECTED
  // ============================================================

  contractSelected(): void {

    const contractNumber =
      this.form.contract_number.trim();


    if (!contractNumber) {

      this.form.contract_id = '';

      this.form.previous_expiry_date = '';

      return;

    }


    const selectedContract =
      this.contracts.find(
        contract =>
          contract.contract_number ===
          contractNumber
      );


    if (!selectedContract) {

      this.form.contract_id = '';

      return;

    }


    this.form.contract_id =
      String(selectedContract.id);


    if (
      selectedContract.end_date
    ) {

      this.form.previous_expiry_date =
        this.formatDate(
          selectedContract.end_date
        );

    }

  }


  // ============================================================
  // GET CONTRACT NUMBER
  // ============================================================

  getContractNumber(
    contractId: number | string
  ): string {

    const contract =
      this.contracts.find(
        x =>
          String(x.id) ===
          String(contractId)
      );


    if (contract) {

      return contract.contract_number;

    }


    return String(contractId);

  }


  // ============================================================
  // SAVE
  // CREATE OR UPDATE
  // ============================================================

  save(): void {

    if (this.saving) {

      return;

    }


    this.error = '';


    // ----------------------------------------------------------
    // Make sure contract exists
    // ----------------------------------------------------------

    if (!this.form.contract_id) {

      this.contractSelected();

    }


    if (!this.form.contract_id) {

      this.error =
        'Please select a valid contract.';

      return;

    }


    // ----------------------------------------------------------
    // Required fields
    // ----------------------------------------------------------

    if (!this.form.renewal_date) {

      this.error =
        'Renewal date is required.';

      return;

    }


    if (!this.form.previous_expiry_date) {

      this.error =
        'Previous expiry date is required.';

      return;

    }


    if (!this.form.new_expiry_date) {

      this.error =
        'New expiry date is required.';

      return;

    }


    // ----------------------------------------------------------
    // Date validation
    // ----------------------------------------------------------

    const renewalDate =
      this.parseDate(
        this.form.renewal_date
      );

    const previousExpiry =
      this.parseDate(
        this.form.previous_expiry_date
      );

    const newExpiry =
      this.parseDate(
        this.form.new_expiry_date
      );


    if (
      !renewalDate ||
      !previousExpiry ||
      !newExpiry
    ) {

      this.error =
        'Please enter valid dates.';

      return;

    }


    // New expiry must be later than renewal date

    if (
      newExpiry.getTime() <=
      renewalDate.getTime()
    ) {

      this.error =
        'New expiry date must be later than the renewal date.';

      return;

    }


    // New expiry must be later than previous expiry

    if (
      newExpiry.getTime() <=
      previousExpiry.getTime()
    ) {

      this.error =
        'New expiry date must be later than the previous expiry date.';

      return;

    }


    // ----------------------------------------------------------
    // CREATE
    // ----------------------------------------------------------

    if (!this.editing) {

      const payload:
        RenewalCreatePayload = {

        contract_id:
          Number(
            this.form.contract_id
          ),

        renewal_date:
          this.form.renewal_date,

        previous_expiry_date:
          this.form.previous_expiry_date,

        new_expiry_date:
          this.form.new_expiry_date,

        notes:
          this.form.notes.trim()

      };


      if (this.form.assigned_to) {

        payload.assigned_to =
          Number(
            this.form.assigned_to
          );

      }


      console.log(
        'Creating renewal:',
        payload
      );


      this.saving = true;


      this.service
        .create(payload)
        .subscribe({

          next: (created) => {

            console.log(
              'Renewal created successfully:',
              created
            );

            this.saving = false;

            this.showForm = false;

            this.editing = undefined;

            this.resetForm();

            this.load();

          },

          error: (e) => {

            console.error(
              'Renewal creation error:',
              e
            );

            this.saving = false;

            this.error =
              this.getErrorMessage(
                e,
                'Unable to create renewal.'
              );

          }

        });

      return;

    }


    // ----------------------------------------------------------
    // UPDATE
    // ----------------------------------------------------------

    const updatePayload:
      RenewalUpdatePayload = {

      renewal_date:
        this.form.renewal_date,

      previous_expiry_date:
        this.form.previous_expiry_date,

      new_expiry_date:
        this.form.new_expiry_date,

      notes:
        this.form.notes.trim()

    };


    if (this.form.assigned_to) {

      updatePayload.assigned_to =
        Number(
          this.form.assigned_to
        );

    }


    console.log(
      'Updating renewal:',
      this.editing.id
    );

    console.log(
      'Update payload:',
      updatePayload
    );


    this.saving = true;


    this.service
      .update(
        this.editing.id,
        updatePayload
      )
      .subscribe({

        next: (updated) => {

          console.log(
            'Renewal updated successfully:',
            updated
          );

          this.saving = false;

          this.showForm = false;

          this.editing = undefined;

          this.resetForm();

          this.load();

        },

        error: (e) => {

          console.error(
            'Renewal update error:',
            e
          );

          this.saving = false;

          this.error =
            this.getErrorMessage(
              e,
              'Unable to update renewal.'
            );

        }

      });

  }


  // ============================================================
  // CHANGE STATUS
  // ============================================================

  change(
    renewal: Renewal,
    newStatus: string
  ): void {

    if (
      !newStatus ||
      newStatus === renewal.status
    ) {

      return;

    }


    this.error = '';


    this.service
      .status(
        renewal.id,
        newStatus
      )
      .subscribe({

        next: () => {

          this.load();

        },

        error: (e) => {

          console.error(
            'Renewal status error:',
            e
          );

          this.error =
            this.getErrorMessage(
              e,
              'Renewal status update failed.'
            );

        }

      });

  }


  // ============================================================
  // COMPLETE RENEWAL
  // ============================================================

  completeRenewal(
    renewal: Renewal
  ): void {

    if (
      renewal.status !==
      'In Progress'
    ) {

      this.error =
        'Only an In Progress renewal can be completed.';

      return;

    }


    const confirmed =
      window.confirm(
        'Complete this renewal and update the contract expiry date?'
      );


    if (!confirmed) {

      return;

    }


    this.error = '';


    this.service
      .complete(
        renewal.id,
        {
          new_expiry_date:
            renewal.new_expiry_date ??
            undefined,

          notes:
            renewal.notes ??
            undefined

        }
      )
      .subscribe({

        next: () => {

          this.load();

          this.loadContracts();

        },

        error: (e) => {

          console.error(
            'Complete renewal error:',
            e
          );

          this.error =
            this.getErrorMessage(
              e,
              'Unable to complete renewal.'
            );

        }

      });

  }


  // ============================================================
  // FORMAT DATE
  // ============================================================

  private formatDate(
    value?: string
  ): string {

    if (!value) {

      return '';

    }

    return value.slice(0, 10);

  }


  // ============================================================
  // PARSE DATE
  // ============================================================

  private parseDate(
    value: string
  ): Date | null {

    if (!value) {

      return null;

    }


    const parts =
      value.split('-');


    if (parts.length !== 3) {

      return null;

    }


    const year =
      Number(parts[0]);

    const month =
      Number(parts[1]) - 1;

    const day =
      Number(parts[2]);


    const date =
      new Date(
        year,
        month,
        day
      );


    if (
      date.getFullYear() !== year ||
      date.getMonth() !== month ||
      date.getDate() !== day
    ) {

      return null;

    }


    return date;

  }


  // ============================================================
  // ERROR MESSAGE
  // ============================================================

  private getErrorMessage(
    error: any,
    fallback: string
  ): string {

    const detail =
      error?.error?.detail;


    // FastAPI 422 validation error

    if (Array.isArray(detail)) {

      return detail
        .map((item: any) => {

          const location =
            Array.isArray(item?.loc)
              ? item.loc
              : [];

          const field =
            location.length > 0
              ? location[
                  location.length - 1
                ]
              : '';

          const message =
            item?.msg ??
            'Invalid value';


          return field
            ? `${field}: ${message}`
            : message;

        })
        .join(' | ');

    }


    // Normal FastAPI error

    if (
      typeof detail ===
      'string'
    ) {

      return detail;

    }


    // Some HTTP clients return message

    if (
      typeof error?.message ===
      'string'
    ) {

      return error.message;

    }


    return fallback;

  }

}
