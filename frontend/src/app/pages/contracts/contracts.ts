import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

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
  selector: 'app-contracts',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink
  ],
  templateUrl: './contracts.html',
  styleUrl: './contracts.scss'
})
export class Contracts implements OnInit {
  private readonly contractService = inject(ContractService);
  private readonly fb = inject(FormBuilder);
  private readonly cdr = inject(ChangeDetectorRef);

  contracts: Contract[] = [];
  loading = true;
  saving = false;
  error = '';
  showForm = false;

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
    this.loadContracts();
  }

  loadContracts(): void {
    this.loading = true;
    this.error = '';

    this.contractService.getContracts().subscribe({
      next: (data) => {
        console.log('Contracts loaded:', data);

        this.contracts = data;
        this.loading = false;

        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Contracts API error:', err);

        this.error = 'Unable to load contracts.';
        this.loading = false;

        this.cdr.detectChanges();
      }
    });
  }

  openCreateForm(): void {
    this.contractForm.reset({
      contract_number: '',
      title: '',
      category: '',
      description: '',
      counterparty_name: '',
      start_date: '',
      end_date: '',
      assigned_to: ''
    });

    this.error = '';
    this.showForm = true;
  }

  cancelCreate(): void {
    this.showForm = false;
    this.error = '';
  }

  createContract(): void {
    if (this.contractForm.invalid) {
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
      counterparty_name: formValue.counterparty_name.trim(),
      start_date: formValue.start_date,
      end_date:
        formValue.end_date.trim() === ''
          ? null
          : formValue.end_date,
      assigned_to: assignedTo
    };

    this.contractService.createContract(payload).subscribe({
      next: (createdContract) => {
        console.log('Contract created:', createdContract);

        this.contracts = [createdContract, ...this.contracts];
        this.showForm = false;
        this.saving = false;

        this.contractForm.reset();

        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Create contract error:', err);

        this.saving = false;

        if (err.status === 409) {
          this.error =
            'A contract with this contract number already exists.';
        } else if (err.status === 400) {
          this.error =
            err.error?.detail ||
            'Invalid contract information.';
        } else {
          this.error = 'Unable to create the contract.';
        }

        this.cdr.detectChanges();
      }
    });
  }

  deleteContract(contract: Contract): void {
    const confirmed = window.confirm(
      `Delete contract "${contract.title}"?`
    );

    if (!confirmed) {
      return;
    }

    this.contractService.deleteContract(contract.id).subscribe({
      next: () => {
        this.contracts = this.contracts.filter(
          item => item.id !== contract.id
        );

        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Delete contract error:', err);

        this.error = 'Unable to delete the contract.';

        this.cdr.detectChanges();
      }
    });
  }
}
