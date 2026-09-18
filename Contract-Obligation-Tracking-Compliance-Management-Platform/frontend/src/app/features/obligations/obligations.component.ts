import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

import { ObligationService } from '../../core/services/obligation.service';
import { ContractService } from '../../core/services/contract.service';

import { Obligation, Contract } from '../../core/models/models';

import { PageHeaderComponent } from '../../shared/page-header.component';
import { StatusComponent } from '../../shared/status.component';
import { EmptyStateComponent } from '../../shared/empty-state.component';

@Component({
  selector: 'cq-obligations',
  standalone: true,
  imports: [
    FormsModule,
    DatePipe,
    PageHeaderComponent,
    StatusComponent,
    EmptyStateComponent
  ],
  templateUrl: './obligations.component.html',
  styleUrl: './obligations.component.css'
})
export class ObligationsComponent {

  private readonly service = inject(ObligationService);
  private readonly contractService = inject(ContractService);

  items: Obligation[] = [];
  filtered: Obligation[] = [];
  contracts: Contract[] = [];

  query = '';
  status = '';

  loading = true;
  saving = false;
  error = '';

  showCreateForm = false;

  statuses = [
    'Pending',
    'In Progress',
    'Delayed',
    'Overdue',
    'Completed'
  ];

  obligationTypes = [
    'Payment Obligation',
    'Delivery Commitment',
    'Reporting Requirement',
    'Renewal Condition',
    'Service Level Agreement',
    'Legal Compliance Requirement'
  ];

  form = {
    contract_id: '',
    title: '',
    description: '',
    obligation_type: '',
    due_date: '',
    assigned_to: ''
  };

  constructor() {
    this.load();
    this.loadContracts();
  }
  loadContracts(): void {
  this.contractService.list().subscribe({
    next: data => {
      this.contracts = data ?? [];
    },
    error: e => {
      this.error =
        e?.error?.detail ||
        'Unable to load contracts.';
    }
  });
}

  load(): void {
    this.loading = true;
    this.error = '';

    this.service.list().subscribe({
      next: data => {
        this.items = data ?? [];
        this.apply();
        this.loading = false;
      },
      error: e => {
        this.error =
          e?.error?.detail ||
          'Unable to load obligations.';
        this.loading = false;
      }
    });
  }

  apply(): void {
  const q = this.query.trim().toLowerCase();

  this.filtered = this.items.filter(x => {

    const contract = this.contracts.find(
      c => String(c.id) === String(x.contract_id)
    );

    const contractNumber =
      contract?.contract_number?.toLowerCase() || '';

    const matchesSearch =
      !q ||
      (x.title || '').toLowerCase().includes(q) ||
      contractNumber.includes(q);

    const matchesStatus =
      !this.status ||
      x.status === this.status;

    return matchesSearch && matchesStatus;
  });
}

  openCreateForm(): void {
    this.error = '';

    this.form = {
      contract_id: '',
      title: '',
      description: '',
      obligation_type: '',
      due_date: '',
      assigned_to: ''
    };

    this.showCreateForm = true;
  }

  closeCreateForm(): void {
    if (this.saving) {
      return;
    }

    this.showCreateForm = false;
  }

  create(): void {

    this.error = '';

    if (!this.form.contract_id) {
      this.error = 'Contract ID is required.';
      return;
    }

    if (!this.form.title.trim()) {
      this.error = 'Obligation title is required.';
      return;
    }

    if (!this.form.obligation_type) {
      this.error = 'Obligation type is required.';
      return;
    }

    if (!this.form.due_date) {
      this.error = 'Due date is required.';
      return;
    }

    const payload: Partial<Obligation> = {
  contract_id: Number(this.form.contract_id),
  title: this.form.title.trim(),
  description: this.form.description.trim(),
  obligation_type: this.form.obligation_type,
  due_date: this.form.due_date
};

if (this.form.assigned_to) {
  payload.assigned_to = Number(this.form.assigned_to);
}

    this.saving = true;

    this.service.create(payload).subscribe({
      next: () => {
        this.saving = false;
        this.showCreateForm = false;
        this.load();
      },
      error: e => {
        this.saving = false;

        this.error =
          e?.error?.detail ||
          'Unable to create obligation.';
      }
    });
  }

  change(
    x: Obligation,
    newStatus: string
  ): void {

    if (!newStatus || newStatus === x.status) {
      return;
    }

    this.error = '';

    this.service.status(x.id, newStatus).subscribe({
      next: () => {
        this.load();
      },
      error: e => {
        this.error =
          e?.error?.detail ||
          'Status update failed.';
      }
    });
  }

  complete(x: Obligation): void {

    if (x.status === 'Completed') {
      return;
    }

    this.error = '';

    this.service.complete(x.id).subscribe({
      next: () => {
        this.load();
      },
      error: e => {
        this.error =
          e?.error?.detail ||
          'Unable to complete obligation.';
      }
    });
  }

  get totalCount(): number {
    return this.items.length;
  }

  get pendingCount(): number {
    return this.items.filter(x => x.status === 'Pending').length;
  }

  get inProgressCount(): number {
    return this.items.filter(x => x.status === 'In Progress').length;
  }

  get completedCount(): number {
    return this.items.filter(x => x.status === 'Completed').length;
  }

    get overdueCount(): number {
    return this.items.filter(x => x.status === 'Overdue').length;
  }

  getContractNumber(contractId: number | string): string {
    const contract = this.contracts.find(
      c => String(c.id) === String(contractId)
    );

    if (!contract) {
      return `#${contractId}`;
    }

    return contract.contract_number;
  }

}
