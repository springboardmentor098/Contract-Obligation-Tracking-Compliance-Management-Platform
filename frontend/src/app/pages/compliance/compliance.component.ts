import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ComplianceService } from '../../core/data.service';
import { ComplianceListItem, ComplianceSummary, HighRiskContract } from '../../core/models';

@Component({
  selector: 'app-compliance',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="page-head">
    <h1>Compliance monitoring</h1>
    <p class="muted">Live status computed from obligation completion across the book of contracts.</p>
  </div>

  <p class="error-banner" *ngIf="error()">{{ error() }}</p>

  <section class="stat-row" *ngIf="summary() as s">
    <div class="stat-card"><span>Total contracts</span><strong>{{ s.total_contracts }}</strong></div>
    <div class="stat-card"><span>Compliant</span><strong>{{ s.compliant_contracts }}</strong></div>
    <div class="stat-card"><span>Delayed</span><strong>{{ s.delayed_contracts }}</strong></div>
    <div class="stat-card stat-card-risk"><span>High risk</span><strong>{{ s.high_risk_contracts }}</strong></div>
  </section>

  <section class="grid-2">
    <article class="panel">
      <div class="panel-head"><h2>By contract</h2></div>
      <table class="ledger" *ngIf="list().length; else noList">
        <thead><tr><th>Contract</th><th>Status</th><th>Score</th></tr></thead>
        <tbody>
          <tr *ngFor="let c of list()">
            <td><a [routerLink]="['/contracts', c.contract_id]" class="docket-num">{{ c.contract_number }}</a></td>
            <td><span class="tag" [ngClass]="tag(c.compliance_status)">{{ c.compliance_status }}</span></td>
            <td>{{ c.compliance_score }}%</td>
          </tr>
        </tbody>
      </table>
      <ng-template #noList><p class="muted" style="padding:16px 20px 20px">No compliance records yet.</p></ng-template>
    </article>

    <article class="panel">
      <div class="panel-head"><h2>High-risk contracts</h2></div>
      <ul class="sub-list" *ngIf="highRisk().length; else noRisk">
        <li *ngFor="let c of highRisk()">
          <a [routerLink]="['/contracts', c.contract_id]" class="docket-num">{{ c.contract_number }}</a>
          <span class="tag tag-rose" style="margin-left:8px">{{ c.risk_level }} risk</span>
          <span class="muted" style="margin-left:8px;font-size:12.5px">{{ c.overdue_obligations }} overdue</span>
        </li>
      </ul>
      <ng-template #noRisk><p class="muted" style="padding:16px 20px 20px">No high-risk contracts right now.</p></ng-template>
    </article>
  </section>
  `,
  styles: [`
    .page-head { margin-bottom: 18px; }
    .stat-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 18px; }
    .stat-card { background: var(--surface); border: 1px solid var(--line); border-left: 3px solid var(--seal); border-radius: var(--radius); padding: 16px 18px; }
    .stat-card-risk { border-left-color: var(--rose); }
    .stat-card span { display: block; font-size: 12.5px; color: var(--ink-soft); }
    .stat-card strong { display: block; font-family: var(--font-display); font-size: 26px; margin-top: 4px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .sub-list { list-style: none; margin: 0; padding: 8px 20px 18px; }
    .sub-list li { padding: 9px 0; border-bottom: 1px solid var(--line); font-size: 13.5px; }
    .sub-list li:last-child { border-bottom: none; }
    @media (max-width: 900px) { .stat-row, .grid-2 { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 600px) { .stat-row, .grid-2 { grid-template-columns: 1fr; } }
  `],
})
export class ComplianceComponent implements OnInit {
  private svc = inject(ComplianceService);
  summary = signal<ComplianceSummary | null>(null);
  list = signal<ComplianceListItem[]>([]);
  highRisk = signal<HighRiskContract[]>([]);
  error = signal('');

  ngOnInit() {
    this.svc.summary().subscribe({ next: s => this.summary.set(s), error: () => this.error.set('Unable to load compliance summary.') });
    this.svc.list().subscribe({ next: l => this.list.set(l), error: () => {} });
    this.svc.highRisk().subscribe({ next: h => this.highRisk.set(h), error: () => {} });
  }

  tag(status: string): string {
    if (status === 'Compliant') return 'tag-seal';
    if (status === 'Pending' || status === 'Delayed') return 'tag-amber';
    return 'tag-rose';
  }
}
