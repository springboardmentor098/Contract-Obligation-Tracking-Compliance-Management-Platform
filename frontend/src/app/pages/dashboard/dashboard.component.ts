import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ReportsService } from '../../core/data.service';
import { AuthService } from '../../core/auth.service';
import { DashboardSummary } from '../../core/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="page-head">
    <div>
      <h1>Docket overview</h1>
      <p class="muted">Good to see you, {{ auth.user()?.full_name?.split(' ')?.[0] }}. Here is where things stand today.</p>
    </div>
  </div>

  <p class="error-banner" *ngIf="error()">{{ error() }}</p>

  <ng-container *ngIf="data() as d">
    <section class="stat-row">
      <a routerLink="/contracts" class="stat-card">
        <span>Active contracts</span>
        <strong>{{ d.contracts.total }}</strong>
        <small>{{ d.contracts.active }} active &middot; {{ d.contracts.expired }} expired</small>
      </a>
      <a routerLink="/obligations" class="stat-card">
        <span>Obligations</span>
        <strong>{{ d.obligations.total }}</strong>
        <small>{{ d.obligations.completed }} completed &middot; {{ d.obligations.overdue }} overdue</small>
      </a>
      <a routerLink="/renewals" class="stat-card">
        <span>Upcoming renewals</span>
        <strong>{{ d.renewals.upcoming }}</strong>
        <small>within the next {{ d.renewals.upcoming_days }} days</small>
      </a>
      <a routerLink="/compliance" class="stat-card stat-card-risk">
        <span>High risk</span>
        <strong>{{ d.compliance.risk_indicators.high }}</strong>
        <small>{{ d.compliance.non_compliant }} non-compliant</small>
      </a>
    </section>

    <section class="grid-2">
      <article class="panel">
        <div class="panel-head"><h2>Contract status</h2></div>
        <div class="bars">
          <div class="bar-row" *ngFor="let s of statusKeys">
            <label>{{ s.label }} <b>{{ d.contracts[s.key] || 0 }}</b></label>
            <div class="bar-track"><div class="bar-fill" [style.width.%]="pct(d.contracts[s.key], d.contracts.total)"></div></div>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head"><h2>Compliance &amp; risk</h2></div>
        <div class="risk-grid">
          <div><b>{{ d.compliance.compliant }}</b><span>Compliant</span></div>
          <div><b>{{ d.compliance.risk_indicators.medium }}</b><span>Medium risk</span></div>
          <div class="danger"><b>{{ d.compliance.risk_indicators.high }}</b><span>High risk</span></div>
        </div>
        <div class="sub-list">
          <h3>High-risk contracts</h3>
          <ul *ngIf="d.compliance.high_risk_contracts?.length; else noRisk">
            <li *ngFor="let c of d.compliance.high_risk_contracts">
              <span class="docket-num">{{ c.contract_number }}</span> — {{ c.contract_title }}
              <span class="tag tag-rose">{{ c.compliance_score }}%</span>
            </li>
          </ul>
          <ng-template #noRisk><p class="muted" style="font-size:13px">No high-risk contracts right now.</p></ng-template>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head"><h2>Approaching expiry</h2></div>
        <ul class="sub-list" *ngIf="d.renewals.approaching_expiry?.length; else noExpiry">
          <li *ngFor="let c of d.renewals.approaching_expiry">
            <span class="docket-num">{{ c.contract_number }}</span> — {{ c.days_remaining }} days remaining
          </li>
        </ul>
        <ng-template #noExpiry><p class="muted" style="padding:16px 20px;font-size:13px">Nothing expiring in the selected window.</p></ng-template>
      </article>

      <article class="panel">
        <div class="panel-head"><h2>Reports</h2><p>Export current data as a document</p></div>
        <div class="export-grid">
          <button class="btn-ghost btn-sm" (click)="download('contracts','excel')">Contracts (Excel)</button>
          <button class="btn-ghost btn-sm" (click)="download('obligations','excel')">Obligations (Excel)</button>
          <button class="btn-ghost btn-sm" (click)="download('renewals','excel')">Renewals (Excel)</button>
          <button class="btn-ghost btn-sm" (click)="download('compliance','pdf')">Compliance (PDF)</button>
        </div>
      </article>
    </section>
  </ng-container>

  <div class="empty-state" *ngIf="!data() && !error()">Loading the register…</div>
  `,
  styles: [`
    .page-head { margin-bottom: 22px; }
    .stat-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 20px; }
    .stat-card {
      background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
      padding: 18px 18px 16px; text-decoration: none; color: var(--ink); display: block;
      border-left: 3px solid var(--seal);
    }
    .stat-card-risk { border-left-color: var(--rose); }
    .stat-card span { display: block; font-size: 12.5px; color: var(--ink-soft); }
    .stat-card strong { display: block; font-family: var(--font-display); font-size: 30px; margin: 6px 0 2px; }
    .stat-card small { color: var(--ink-soft); font-size: 12.5px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .bars { padding: 6px 20px 18px; }
    .bar-row { margin: 14px 0; }
    .bar-row label { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px; }
    .bar-track { height: 6px; background: var(--slate-soft); border-radius: 4px; overflow: hidden; }
    .bar-fill { height: 100%; background: var(--seal); }
    .risk-grid { display: flex; gap: 10px; padding: 16px 20px 4px; }
    .risk-grid > div { flex: 1; border: 1px solid var(--line); border-radius: var(--radius); padding: 12px; text-align: center; }
    .risk-grid .danger { border-color: #e3bcb7; background: var(--rose-soft); }
    .risk-grid b { display: block; font-family: var(--font-display); font-size: 22px; }
    .risk-grid span { font-size: 12px; color: var(--ink-soft); }
    .sub-list { padding: 8px 20px 18px; }
    .sub-list h3 { font-size: 13px; color: var(--ink-soft); font-weight: 500; font-family: var(--font-body); margin-bottom: 8px; }
    .sub-list ul { list-style: none; margin: 0; padding: 0; }
    .sub-list li { display: flex; align-items: center; gap: 8px; font-size: 13.5px; padding: 7px 0; border-bottom: 1px solid var(--line); }
    .sub-list li:last-child { border-bottom: none; }
    .export-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 16px 20px 20px; }
    @media (max-width: 900px) { .stat-row, .grid-2 { grid-template-columns: 1fr; } }
  `],
})
export class DashboardComponent implements OnInit {
  private reports = inject(ReportsService);
  auth = inject(AuthService);
  data = signal<DashboardSummary | null>(null);
  error = signal('');

  statusKeys = [
    { key: 'active', label: 'Active' },
    { key: 'draft', label: 'Draft' },
    { key: 'under_review', label: 'Under review' },
    { key: 'approved', label: 'Approved' },
    { key: 'expired', label: 'Expired' },
    { key: 'terminated', label: 'Terminated' },
  ];

  ngOnInit() {
    this.reports.dashboard().subscribe({
      next: d => this.data.set(d),
      error: () => this.error.set('Unable to load the dashboard summary.'),
    });
  }

  pct(v: number, total: number): number {
    if (!total) return 0;
    return Math.min(100, Math.round((v / total) * 100));
  }

  download(kind: string, fmt: 'excel' | 'pdf') {
    this.reports.export(kind, fmt).subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contractiq_${kind}_report.${fmt === 'excel' ? 'xlsx' : 'pdf'}`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }
}
