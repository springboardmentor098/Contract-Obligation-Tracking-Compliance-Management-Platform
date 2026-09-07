import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ContractsService } from '../../core/data.service';
import { ContractListItem } from '../../core/models';

@Component({
  selector: 'app-contract-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="page-head">
    <div>
      <h1>Contract repository</h1>
      <p class="muted">{{ filtered().length }} of {{ contracts().length }} contracts</p>
    </div>
    <a routerLink="/contracts/new" class="btn">New contract</a>
  </div>

  <div class="filters">
    <input placeholder="Search title or contract number…" [(ngModel)]="query" />
    <select [(ngModel)]="statusFilter">
      <option value="">All statuses</option>
      <option *ngFor="let s of statuses" [value]="s">{{ s }}</option>
    </select>
    <select [(ngModel)]="categoryFilter">
      <option value="">All categories</option>
      <option *ngFor="let c of categories" [value]="c">{{ c }}</option>
    </select>
  </div>

  <p class="error-banner" *ngIf="error()">{{ error() }}</p>

  <div class="panel" *ngIf="filtered().length; else empty">
    <table class="ledger">
      <thead>
        <tr><th>Docket #</th><th>Title</th><th>Category</th><th>Status</th><th>End date</th><th></th></tr>
      </thead>
      <tbody>
        <tr *ngFor="let c of filtered()">
          <td class="docket-num">{{ c.contract_number }}</td>
          <td>{{ c.title }}</td>
          <td>{{ c.category }}</td>
          <td><span class="tag" [ngClass]="statusTag(c.status)">{{ c.status }}</span></td>
          <td>{{ c.end_date | date:'mediumDate' }}</td>
          <td><a [routerLink]="['/contracts', c.id]" class="btn-ghost btn-sm">Open</a></td>
        </tr>
      </tbody>
    </table>
  </div>
  <ng-template #empty>
    <div class="panel empty-state">
      <strong>No contracts match</strong>
      Try clearing the filters, or add the first contract to the repository.
    </div>
  </ng-template>
  `,
  styles: [`
    .page-head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; gap: 12px; }
    .filters { display: flex; gap: 10px; margin-bottom: 16px; }
    .filters input { flex: 1; border: 1px solid var(--line-strong); border-radius: var(--radius); padding: 9px 12px; background: var(--surface); }
    .filters select { border: 1px solid var(--line-strong); border-radius: var(--radius); padding: 9px 12px; background: var(--surface); }
  `],
})
export class ContractListComponent implements OnInit {
  private svc = inject(ContractsService);
  contracts = signal<ContractListItem[]>([]);
  error = signal('');
  query = '';
  statusFilter = '';
  categoryFilter = '';

  statuses = ['Draft', 'Under Review', 'Approved', 'Active', 'Expired', 'Terminated'];
  categories = ['Employment Contract', 'Vendor Contract', 'Service Agreement', 'Lease Agreement', 'Purchase Agreement', 'Partnership Agreement', 'Confidentiality Agreement'];

  filtered(): ContractListItem[] {
    const q = this.query.trim().toLowerCase();
    return this.contracts().filter(c => {
      if (this.statusFilter && c.status !== this.statusFilter) return false;
      if (this.categoryFilter && c.category !== this.categoryFilter) return false;
      if (q && !`${c.title} ${c.contract_number}`.toLowerCase().includes(q)) return false;
      return true;
    });
  }

  ngOnInit() {
    this.svc.list().subscribe({
      next: list => this.contracts.set(list),
      error: () => this.error.set('Unable to load contracts.'),
    });
  }

  statusTag(status: string): string {
    if (status === 'Active' || status === 'Approved') return 'tag-seal';
    if (status === 'Under Review' || status === 'Draft') return 'tag-amber';
    if (status === 'Expired' || status === 'Terminated') return 'tag-rose';
    return 'tag-slate';
  }
}
