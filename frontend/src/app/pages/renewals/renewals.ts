import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

import {
  Renewal,
  RenewalService
} from '../../core/services/renewal.service';

import {
  Contract,
  ContractService
} from '../../core/services/contract.service';

interface RenewalRow extends Renewal {
  contract_number: string;
  contract_title: string;
}

@Component({
  selector: 'app-renewals',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './renewals.html',
  styleUrl: './renewals.scss'
})
export class Renewals implements OnInit {
  private readonly renewalService = inject(RenewalService);
  private readonly contractService = inject(ContractService);
  private readonly fb = inject(FormBuilder);
  private readonly cdr = inject(ChangeDetectorRef);

  renewals: RenewalRow[] = [];
  contracts: Contract[] = [];

  loading = true;
  saving = false;
  showForm = false;
  editingId: number | null = null;
  error = '';
  success = '';

  renewalForm = this.fb.nonNullable.group({
    contract_id: [0, [Validators.required, Validators.min(1)]],
    renewal_date: ['', [Validators.required]],
    status: ['upcoming', [Validators.required]],
    renewal_terms: ['']
  });

  ngOnInit(): void {
    this.loadRenewals();
  }

  loadRenewals(): void {
    this.loading = true;
    this.error = '';
    this.success = '';

    this.contractService.getContracts().subscribe({
      next: (contracts) => {
        this.contracts = contracts;

        if (!contracts.length) {
          this.renewals = [];
          this.loading = false;
          this.cdr.detectChanges();
          return;
        }

        const requests = contracts.map(contract =>
          this.renewalService.getContractRenewals(contract.id).pipe(
            catchError(() => of([] as Renewal[]))
          )
        );

        forkJoin(requests).subscribe({
          next: (results) => {
            const rows: RenewalRow[] = [];

            results.forEach((renewalList, index) => {
              const contract = contracts[index];

              renewalList.forEach((renewal) => {
                rows.push({
                  ...renewal,
                  contract_number: contract.contract_number,
                  contract_title: contract.title
                });
              });
            });

            this.renewals = rows.sort(
              (a, b) =>
                new Date(a.renewal_date).getTime() -
                new Date(b.renewal_date).getTime()
            );

            this.loading = false;
            this.cdr.detectChanges();
          },
          error: () => {
            this.error = 'Unable to load renewals.';
            this.loading = false;
            this.cdr.detectChanges();
          }
        });
      },
      error: () => {
        this.error = 'Unable to load contracts.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  openCreateForm(): void {
    this.editingId = null;
    this.success = '';
    this.error = '';

    this.renewalForm.reset({
      contract_id: this.contracts.length ? this.contracts[0].id : 0,
      renewal_date: '',
      status: 'upcoming',
      renewal_terms: ''
    });

    this.showForm = true;
    this.cdr.detectChanges();
  }

  openEdit(renewal: RenewalRow): void {
    this.editingId = renewal.id;
    this.success = '';
    this.error = '';

    this.renewalForm.patchValue({
      contract_id: renewal.contract_id,
      renewal_date: renewal.renewal_date,
      status: renewal.status,
      renewal_terms: renewal.renewal_terms ?? ''
    });

    this.showForm = true;
    this.cdr.detectChanges();
  }

  cancelForm(): void {
    this.showForm = false;
    this.editingId = null;
    this.error = '';
    this.cdr.detectChanges();
  }

  saveRenewal(): void {
    if (this.renewalForm.invalid || this.saving) {
      this.renewalForm.markAllAsTouched();
      return;
    }

    this.saving = true;
    this.error = '';
    this.success = '';

    const value = this.renewalForm.getRawValue();

    if (this.editingId !== null) {
      this.renewalService.updateRenewal(this.editingId, {
        renewal_date: value.renewal_date,
        status: value.status,
        renewal_terms: value.renewal_terms || null
      }).subscribe({
        next: () => {
          this.saving = false;
          this.showForm = false;
          this.editingId = null;
          this.success = 'Renewal updated successfully.';
          this.loadRenewals();
        },
        error: (err) => {
          this.saving = false;
          this.error = err?.error?.detail || 'Unable to update renewal.';
          this.cdr.detectChanges();
        }
      });

      return;
    }

    this.renewalService.createRenewal(value.contract_id, {
      renewal_date: value.renewal_date,
      status: value.status,
      renewal_terms: value.renewal_terms || null
    }).subscribe({
      next: () => {
        this.saving = false;
        this.showForm = false;
        this.success = 'Renewal created successfully.';
        this.loadRenewals();
      },
      error: (err) => {
        this.saving = false;
        this.error = err?.error?.detail || 'Unable to create renewal.';
        this.cdr.detectChanges();
      }
    });
  }

  deleteRenewal(renewal: RenewalRow): void {
    if (!window.confirm(
      `Delete renewal for ${renewal.contract_number}?`
    )) {
      return;
    }

    this.renewalService.deleteRenewal(renewal.id).subscribe({
      next: () => {
        this.success = 'Renewal deleted successfully.';
        this.loadRenewals();
      },
      error: (err) => {
        this.error = err?.error?.detail || 'Unable to delete renewal.';
        this.cdr.detectChanges();
      }
    });
  }

  get upcomingCount(): number {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return this.renewals.filter(r =>
      new Date(r.renewal_date) >= today &&
      r.status.toLowerCase() !== 'completed'
    ).length;
  }

  get completedCount(): number {
    return this.renewals.filter(
      r => r.status.toLowerCase() === 'completed'
    ).length;
  }
}
