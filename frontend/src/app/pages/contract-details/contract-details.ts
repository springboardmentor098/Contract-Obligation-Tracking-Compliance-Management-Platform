import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import {
  Contract,
  ContractService
} from '../../core/services/contract.service';

@Component({
  selector: 'app-contract-details',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './contract-details.html',
  styleUrl: './contract-details.scss'
})
export class ContractDetails implements OnInit {

  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly contractService = inject(ContractService);
  private readonly fb = inject(FormBuilder);
  private readonly cdr = inject(ChangeDetectorRef);

  contract: Contract | null = null;

  loading = true;
  saving = false;
  workflowSaving = false;

  error = '';
  workflowError = '';

  editMode = false;

  contractForm = this.fb.nonNullable.group({
    contract_number: ['', [Validators.required]],
    title: ['', [Validators.required]],
    category: ['', [Validators.required]],
    description: [''],
    counterparty_name: ['', [Validators.required]],
    start_date: ['', [Validators.required]],
    end_date: [''],
    assigned_to: ['']
  });

  ngOnInit(): void {
    const id = Number(
      this.route.snapshot.paramMap.get('id')
    );

    if (!id) {
      this.error = 'Invalid contract ID.';
      this.loading = false;
      return;
    }

    this.loadContract(id);
  }

  loadContract(id: number): void {
    this.loading = true;
    this.error = '';

    this.contractService.getContract(id).subscribe({
      next: (data) => {
        console.log('Contract details:', data);

        this.contract = data;
        this.loading = false;

        this.cdr.detectChanges();
      },

      error: (err) => {
        console.error('Contract details error:', err);

        this.error =
          err.status === 404
            ? 'Contract not found.'
            : 'Unable to load contract details.';

        this.loading = false;

        this.cdr.detectChanges();
      }
    });
  }

  openEdit(): void {
    if (!this.contract) {
      return;
    }

    this.contractForm.reset({
      contract_number: this.contract.contract_number,
      title: this.contract.title,
      category: this.contract.category,
      description: this.contract.description ?? '',
      counterparty_name: this.contract.counterparty_name,
      start_date: this.contract.start_date,
      end_date: this.contract.end_date ?? '',
      assigned_to:
        this.contract.assigned_to !== null
          ? String(this.contract.assigned_to)
          : ''
    });

    this.error = '';
    this.editMode = true;

    this.cdr.detectChanges();
  }

  cancelEdit(): void {
    this.editMode = false;
    this.error = '';
  }

  saveContract(): void {
    if (!this.contract || this.contractForm.invalid) {
      this.contractForm.markAllAsTouched();
      return;
    }

    this.saving = true;
    this.error = '';

    const formValue = this.contractForm.getRawValue();

    const assignedTo =
      formValue.assigned_to.trim() === ''
        ? null
        : Number(formValue.assigned_to);

    const payload = {
      contract_number: formValue.contract_number.trim(),
      title: formValue.title.trim(),
      category: formValue.category.trim(),
      description:
        formValue.description.trim() === ''
          ? null
          : formValue.description.trim(),
      counterparty_name:
        formValue.counterparty_name.trim(),
      start_date: formValue.start_date,
      end_date:
        formValue.end_date.trim() === ''
          ? null
          : formValue.end_date,
      assigned_to: assignedTo
    };

    this.contractService
      .updateContract(this.contract.id, payload)
      .subscribe({
        next: (updatedContract) => {
          console.log(
            'Contract updated:',
            updatedContract
          );

          this.contract = updatedContract;
          this.editMode = false;
          this.saving = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'Update contract error:',
            err
          );

          this.saving = false;

          if (err.status === 409) {
            this.error =
              'A contract with this contract number already exists.';
          } else if (err.status === 400) {
            this.error =
              err.error?.detail ||
              'Invalid contract information.';
          } else if (err.status === 403) {
            this.error =
              'You do not have permission to edit this contract.';
          } else {
            this.error =
              'Unable to update the contract.';
          }

          this.cdr.detectChanges();
        }
      });
  }

  changeStatus(newStatus: string): void {
    if (!this.contract || this.workflowSaving) {
      return;
    }

    const confirmed = window.confirm(
      `Change contract status from "${this.contract.status}" to "${newStatus}"?`
    );

    if (!confirmed) {
      return;
    }

    this.workflowSaving = true;
    this.workflowError = '';

    this.contractService
      .updateStatus(this.contract.id, newStatus)
      .subscribe({
        next: (updatedContract) => {
          console.log(
            'Contract status updated:',
            updatedContract
          );

          this.contract = updatedContract;
          this.workflowSaving = false;

          this.cdr.detectChanges();
        },

        error: (err) => {
          console.error(
            'Contract status update error:',
            err
          );

          this.workflowSaving = false;

          if (err.status === 403) {
            this.workflowError =
              'You do not have permission to perform this status change.';
          } else if (err.status === 400) {
            this.workflowError =
              err.error?.detail ||
              'Invalid status transition.';
          } else if (err.status === 404) {
            this.workflowError =
              'Contract not found.';
          } else {
            this.workflowError =
              'Unable to update contract status.';
          }

          this.cdr.detectChanges();
        }
      });
  }

  goBack(): void {
    this.router.navigate(['/contracts']);
  }
}
