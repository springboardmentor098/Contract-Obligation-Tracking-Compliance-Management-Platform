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
  ObligationsService,
  Obligation,
  ObligationCreate
} from '../services/obligations';

import {
  ContractsService,
  Contract
} from '../services/contracts';

@Component({
  selector: 'app-obligations',
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
  templateUrl: './obligations.html',
  styleUrl: './obligations.css'
})
export class Obligations implements OnInit {

  obligations: Obligation[] = [];
  filteredObligations: Obligation[] = [];
  contracts: Contract[] = [];

  loading = false;
  saving = false;

  errorMessage = '';
  successMessage = '';

  searchText = '';
  selectedStatus = '';

  showForm = false;
  editingObligation: Obligation | null = null;
  selectedObligation: Obligation | null = null;

  displayedColumns = [
    'title',
    'contract_id',
    'obligation_type',
    'due_date',
    'assigned_to',
    'status',
    'actions'
  ];

  statuses = [
    'Pending',
    'In Progress',
    'Completed',
    'Overdue'
  ];

  obligationForm!: FormGroup;

  constructor(
    private formBuilder: FormBuilder,
    private obligationsService: ObligationsService,
    private contractsService: ContractsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {

    this.obligationForm = this.formBuilder.group({
      title: ['', Validators.required],
      description: [''],
      obligation_type: ['', Validators.required],
      due_date: ['', Validators.required],
      assigned_to: ['', Validators.required],
      contract_id: ['', Validators.required]
    });

    this.loadContracts();
    this.loadObligations();
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

  loadObligations(): void {
    this.loading = true;
    this.errorMessage = '';

    this.obligationsService.getObligations().subscribe({
      next: (data) => {
        this.obligations = data;
        this.applyFilters();
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Obligations API error:', error);
        this.errorMessage = 'Unable to load obligations.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  applyFilters(): void {

    const search = this.searchText
      .toLowerCase()
      .trim();

    this.filteredObligations =
      this.obligations.filter(obligation => {

        const matchesSearch =
          !search ||
          obligation.title.toLowerCase().includes(search) ||
          obligation.obligation_type.toLowerCase().includes(search) ||
          String(obligation.contract_id).includes(search);

        const matchesStatus =
          !this.selectedStatus ||
          obligation.status === this.selectedStatus;

        return matchesSearch && matchesStatus;
      });
  }

  openCreateForm(): void {

    this.editingObligation = null;
    this.obligationForm.reset();

    this.showForm = true;
    this.errorMessage = '';
    this.successMessage = '';
  }

  openEditForm(obligation: Obligation): void {

    this.editingObligation = obligation;

    this.obligationForm.patchValue({
      title: obligation.title,
      description: obligation.description || '',
      obligation_type: obligation.obligation_type,
      due_date: obligation.due_date,
      assigned_to: obligation.assigned_to,
      contract_id: obligation.contract_id
    });

    this.showForm = true;
    this.errorMessage = '';
    this.successMessage = '';
  }

  cancelForm(): void {

    this.showForm = false;
    this.editingObligation = null;

    this.obligationForm.reset();
  }

  saveObligation(): void {

    if (this.obligationForm.invalid) {
      this.obligationForm.markAllAsTouched();
      return;
    }

    const formValue =
      this.obligationForm.getRawValue();

    this.saving = true;
    this.errorMessage = '';
    this.successMessage = '';

    if (this.editingObligation) {

      const updateData = {
        title: formValue.title,
        description:
          formValue.description || undefined,
        obligation_type:
          formValue.obligation_type,
        due_date:
          formValue.due_date,
        assigned_to:
          Number(formValue.assigned_to)
      };

      this.obligationsService.updateObligation(
        this.editingObligation.id,
        updateData
      ).subscribe({

        next: () => {

          this.saving = false;
          this.successMessage =
            'Obligation updated successfully.';

          this.showForm = false;
          this.editingObligation = null;

          this.obligationForm.reset();

          this.loadObligations();
        },

        error: (error) => {

          console.error(
            'Update obligation error:',
            error
          );

          this.saving = false;

          this.errorMessage =
            error.error?.detail ||
            'Unable to update obligation.';

          this.cdr.markForCheck();
        }
      });

    } else {

      const obligationData: ObligationCreate = {
        title: formValue.title,
        description:
          formValue.description || undefined,
        obligation_type:
          formValue.obligation_type,
        due_date:
          formValue.due_date,
        assigned_to:
          Number(formValue.assigned_to),
        contract_id:
          Number(formValue.contract_id)
      };

      this.obligationsService.createObligation(
        obligationData
      ).subscribe({

        next: () => {

          this.saving = false;

          this.successMessage =
            'Obligation created successfully.';

          this.showForm = false;

          this.obligationForm.reset();

          this.loadObligations();
        },

        error: (error) => {

          console.error(
            'Create obligation error:',
            error
          );

          this.saving = false;

          this.errorMessage =
            error.error?.detail ||
            'Unable to create obligation.';

          this.cdr.markForCheck();
        }
      });
    }
  }

  viewObligation(
    obligation: Obligation
  ): void {

    this.loading = true;
    this.errorMessage = '';

    this.obligationsService.getObligation(
      obligation.id
    ).subscribe({

      next: (data) => {

        this.selectedObligation = data;

        this.loading = false;

        this.cdr.markForCheck();
      },

      error: (error) => {

        console.error(
          'Obligation details error:',
          error
        );

        this.errorMessage =
          'Unable to load obligation details.';

        this.loading = false;

        this.cdr.markForCheck();
      }
    });
  }

  closeDetails(): void {
    this.selectedObligation = null;
  }

  updateStatus(
    obligation: Obligation,
    status: string
  ): void {

    this.obligationsService.updateStatus(
      obligation.id,
      status
    ).subscribe({

      next: () => {

        this.successMessage =
          'Obligation status updated successfully.';

        this.loadObligations();
      },

      error: (error) => {

        console.error(
          'Obligation status error:',
          error
        );

        this.errorMessage =
          error.error?.detail ||
          'Unable to update obligation status.';

        this.cdr.markForCheck();
      }
    });
  }

  completeObligation(
    obligation: Obligation
  ): void {

    this.obligationsService.completeObligation(
      obligation.id
    ).subscribe({

      next: () => {

        this.successMessage =
          'Obligation completed successfully.';

        this.loadObligations();
      },

      error: (error) => {

        console.error(
          'Complete obligation error:',
          error
        );

        this.errorMessage =
          error.error?.detail ||
          'Unable to complete obligation.';

        this.cdr.markForCheck();
      }
    });
  }

  getContractTitle(contractId: number): string {

    const contract = this.contracts.find(
      item => item.id === contractId
    );

    return contract
      ? contract.title
      : `Contract #${contractId}`;
  }
}
