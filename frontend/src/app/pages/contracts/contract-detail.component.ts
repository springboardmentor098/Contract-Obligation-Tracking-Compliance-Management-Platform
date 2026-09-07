import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ContractsService, ObligationsService, RenewalsService } from '../../core/data.service';
import { Contract, ObligationListItem, Renewal, ContractCompliance } from '../../core/models';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-contract-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <ng-container *ngIf="contract() as c">
    <div class="page-head">
      <div>
        <span class="docket-num">{{ c.contract_number }}</span>
        <h1>{{ c.title }}</h1>
        <span class="tag" [ngClass]="statusTag(c.status)">{{ c.status }}</span>
      </div>
      <div class="actions">
        <a [routerLink]="['/contracts', c.id, 'edit']" class="btn-ghost">Edit</a>
        <button class="btn-ghost" *ngIf="c.status === 'Draft'" (click)="run(svc.submitReview(c.id))">Submit for review</button>
        <button class="btn-ghost" *ngIf="c.status === 'Under Review'" (click)="run(svc.approve(c.id))">Approve</button>
        <button class="btn" *ngIf="c.status === 'Approved'" (click)="run(svc.activate(c.id))">Activate</button>
      </div>
    </div>

    <p class="error-banner" *ngIf="error()">{{ error() }}</p>

    <section class="grid-2">
      <article class="panel">
        <div class="panel-head"><h2>Terms</h2></div>
        <dl class="deflist">
          <div><dt>Category</dt><dd>{{ c.category }}</dd></div>
          <div><dt>Start date</dt><dd>{{ c.start_date | date:'mediumDate' }}</dd></div>
          <div><dt>End date</dt><dd>{{ c.end_date | date:'mediumDate' }}</dd></div>
          <div><dt>Description</dt><dd>{{ c.description || '—' }}</dd></div>
        </dl>
      </article>

      <article class="panel" *ngIf="compliance() as comp">
        <div class="panel-head"><h2>Compliance</h2></div>
        <div class="comp-body">
          <div class="comp-score">
            <strong>{{ comp.compliance_score }}%</strong>
            <span class="tag" [ngClass]="complianceTag(comp.compliance_status)">{{ comp.compliance_status }}</span>
          </div>
          <ul class="sub-list-flat">
            <li>{{ comp.completed_obligations }} completed</li>
            <li>{{ comp.pending_obligations }} pending</li>
            <li>{{ comp.overdue_obligations }} overdue</li>
            <li>Risk: {{ comp.risk_level }}</li>
          </ul>
        </div>
      </article>
    </section>

    <section class="panel" style="margin-top:14px">
      <div class="panel-head"><h2>Obligations</h2><a [routerLink]="['/obligations/new']" [queryParams]="{contractId: c.id}" class="btn-sm btn-ghost">Add obligation</a></div>
      <table class="ledger" *ngIf="obligations().length; else noObl">
        <thead><tr><th>Title</th><th>Type</th><th>Due</th><th>Status</th></tr></thead>
        <tbody>
          <tr *ngFor="let o of obligations()">
            <td>{{ o.title }}</td><td>{{ o.obligation_type }}</td>
            <td>{{ o.due_date | date:'mediumDate' }}</td>
            <td><span class="tag" [ngClass]="obligationTag(o.status)">{{ o.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <ng-template #noObl><p class="muted" style="padding:16px 20px 20px">No obligations recorded for this contract yet.</p></ng-template>
    </section>

    <section class="panel" style="margin-top:14px">
      <div class="panel-head"><h2>Renewals</h2></div>
      <table class="ledger" *ngIf="renewals().length; else noRen">
        <thead><tr><th>Renewal date</th><th>New expiry</th><th>Status</th></tr></thead>
        <tbody>
          <tr *ngFor="let r of renewals()">
            <td>{{ r.renewal_date | date:'mediumDate' }}</td>
            <td>{{ r.new_expiry_date | date:'mediumDate' }}</td>
            <td><span class="tag tag-slate">{{ r.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <ng-template #noRen><p class="muted" style="padding:16px 20px 20px">No renewal history yet.</p></ng-template>
    </section>
  </ng-container>

  <div class="empty-state" *ngIf="!contract() && !error()">Loading contract…</div>
  `,
  styles: [`
    .page-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; gap: 12px; }
    .page-head h1 { margin: 4px 0 8px; }
    .actions { display: flex; gap: 8px; flex-shrink: 0; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .deflist { padding: 6px 20px 18px; margin: 0; }
    .deflist > div { display: flex; gap: 14px; padding: 8px 0; border-bottom: 1px solid var(--line); }
    .deflist > div:last-child { border-bottom: none; }
    .deflist dt { flex: 0 0 110px; color: var(--ink-soft); font-size: 13px; }
    .deflist dd { margin: 0; font-size: 13.5px; }
    .comp-body { padding: 10px 20px 18px; }
    .comp-score { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
    .comp-score strong { font-family: var(--font-display); font-size: 30px; }
    .sub-list-flat { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 8px 16px; font-size: 13px; color: var(--ink-soft); }
    @media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
  `],
})
export class ContractDetailComponent implements OnInit {
  svc = inject(ContractsService);
  private obligationsSvc = inject(ObligationsService);
  private renewalsSvc = inject(RenewalsService);
  private route = inject(ActivatedRoute);
  auth = inject(AuthService);

  contract = signal<Contract | null>(null);
  compliance = signal<ContractCompliance | null>(null);
  obligations = signal<ObligationListItem[]>([]);
  renewals = signal<Renewal[]>([]);
  error = signal('');
  private id!: number;

  ngOnInit() {
    this.id = Number(this.route.snapshot.paramMap.get('id'));
    this.load();
  }

  load() {
    this.svc.get(this.id).subscribe({ next: c => this.contract.set(c), error: () => this.error.set('Unable to load this contract.') });
    this.svc.compliance(this.id).subscribe({ next: c => this.compliance.set(c), error: () => {} });
    this.obligationsSvc.forContract(this.id).subscribe({ next: o => this.obligations.set(o), error: () => {} });
    this.renewalsSvc.forContract(this.id).subscribe({ next: r => this.renewals.set(r), error: () => {} });
  }

  run(obs: any) {
    this.error.set('');
    obs.subscribe({
      next: () => this.load(),
      error: (e: any) => this.error.set(e.error?.detail ? String(e.error.detail) : 'That action could not be completed.'),
    });
  }

  statusTag(status: string): string {
    if (status === 'Active' || status === 'Approved') return 'tag-seal';
    if (status === 'Under Review' || status === 'Draft') return 'tag-amber';
    if (status === 'Expired' || status === 'Terminated') return 'tag-rose';
    return 'tag-slate';
  }
  complianceTag(status: string): string {
    if (status === 'Compliant') return 'tag-seal';
    if (status === 'Pending' || status === 'Delayed') return 'tag-amber';
    return 'tag-rose';
  }
  obligationTag(status: string): string {
    if (status === 'Completed') return 'tag-seal';
    if (status === 'Pending' || status === 'In Progress') return 'tag-slate';
    if (status === 'Delayed') return 'tag-amber';
    return 'tag-rose';
  }
}
