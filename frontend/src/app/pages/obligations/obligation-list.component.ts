import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ObligationsService } from '../../core/data.service';
import { ObligationListItem } from '../../core/models';

@Component({
  selector: 'app-obligation-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="page-head">
    <div>
      <h1>Obligations</h1>
      <p class="muted">{{ filtered().length }} of {{ obligations().length }} tracked</p>
    </div>
    <a routerLink="/obligations/new" class="btn">Register obligation</a>
  </div>

  <div class="filters">
    <input placeholder="Search title…" [(ngModel)]="query" />
    <select [(ngModel)]="statusFilter">
      <option value="">All statuses</option>
      <option *ngFor="let s of statuses" [value]="s">{{ s }}</option>
    </select>
  </div>

  <p class="error-banner" *ngIf="error()">{{ error() }}</p>

  <div class="panel" *ngIf="filtered().length; else empty">
    <table class="ledger">
      <thead><tr><th>Title</th><th>Contract</th><th>Type</th><th>Due date</th><th>Status</th><th></th></tr></thead>
      <tbody>
        <tr *ngFor="let o of filtered()">
          <td>{{ o.title }}</td>
          <td><a [routerLink]="['/contracts', o.contract_id]" class="docket-num">#{{ o.contract_id }}</a></td>
          <td>{{ o.obligation_type }}</td>
          <td [class.overdue-text]="isOverdue(o)">{{ o.due_date | date:'mediumDate' }}</td>
          <td><span class="tag" [ngClass]="tag(o.status)">{{ o.status }}</span></td>
          <td>
            <button class="btn-ghost btn-sm" *ngIf="o.status !== 'Completed'" (click)="complete(o)">Mark complete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <ng-template #empty>
    <div class="panel empty-state">
      <strong>No obligations match</strong>
      Register a payment, delivery, reporting, or compliance obligation against a contract.
    </div>
  </ng-template>
  `,
  styles: [`
    .page-head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; }
    .filters { display: flex; gap: 10px; margin-bottom: 16px; }
    .filters input { flex: 1; border: 1px solid var(--line-strong); border-radius: var(--radius); padding: 9px 12px; background: var(--surface); }
    .filters select { border: 1px solid var(--line-strong); border-radius: var(--radius); padding: 9px 12px; background: var(--surface); }
    .overdue-text { color: var(--rose); font-weight: 500; }
  `],
})
export class ObligationListComponent implements OnInit {
  private svc = inject(ObligationsService);
  obligations = signal<ObligationListItem[]>([]);
  error = signal('');
  query = '';
  statusFilter = '';
  statuses = ['Pending', 'In Progress', 'Completed', 'Delayed', 'Overdue'];

  ngOnInit() {
    this.svc.list().subscribe({
      next: list => this.obligations.set(list),
      error: () => this.error.set('Unable to load obligations.'),
    });
  }

  filtered(): ObligationListItem[] {
    const q = this.query.trim().toLowerCase();
    return this.obligations().filter(o => {
      if (this.statusFilter && o.status !== this.statusFilter) return false;
      if (q && !o.title.toLowerCase().includes(q)) return false;
      return true;
    });
  }

  isOverdue(o: ObligationListItem): boolean {
    return o.status !== 'Completed' && new Date(o.due_date) < new Date(new Date().toDateString());
  }

  tag(status: string): string {
    if (status === 'Completed') return 'tag-seal';
    if (status === 'Pending' || status === 'In Progress') return 'tag-slate';
    if (status === 'Delayed') return 'tag-amber';
    return 'tag-rose';
  }

  complete(o: ObligationListItem) {
    this.svc.complete(o.id).subscribe({
      next: updated => this.obligations.set(this.obligations().map(x => x.id === updated.id ? { ...x, status: updated.status } : x)),
      error: () => this.error.set('Unable to mark that obligation complete.'),
    });
  }
}
