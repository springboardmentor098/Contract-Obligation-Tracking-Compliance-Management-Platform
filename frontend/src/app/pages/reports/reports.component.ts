import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReportsService } from '../../core/data.service';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule],
  template: `
  <div class="page-head">
    <h1>Reports</h1>
    <p class="muted">Summaries drawn from the live register, with PDF and Excel export.</p>
  </div>

  <section class="grid-2">
    <article class="panel" *ngFor="let r of reportCards">
      <div class="panel-head">
        <h2>{{ r.title }}</h2>
        <p>{{ r.description }}</p>
      </div>
      <div class="summary-body" *ngIf="summaries[r.kind] as s">
        <div *ngFor="let entry of objectEntries(s)"><span>{{ entry[0] | titlecase }}</span><b>{{ entry[1] }}</b></div>
      </div>
      <div class="export-row">
        <button class="btn-ghost btn-sm" (click)="download(r.kind, 'excel')">Export Excel</button>
        <button class="btn-ghost btn-sm" (click)="download(r.kind, 'pdf')">Export PDF</button>
      </div>
    </article>
  </section>
  `,
  styles: [`
    .page-head { margin-bottom: 18px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .summary-body { padding: 6px 20px 4px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; }
    .summary-body > div { display: flex; justify-content: space-between; font-size: 13px; padding: 6px 0; border-bottom: 1px solid var(--line); }
    .summary-body b { font-family: var(--font-mono); font-weight: 500; }
    .export-row { display: flex; gap: 8px; padding: 14px 20px 20px; }
    @media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
  `],
})
export class ReportsComponent implements OnInit {
  private svc = inject(ReportsService);
  summaries: Record<string, any> = {};

  reportCards = [
    { kind: 'contracts', title: 'Contracts', description: 'Status breakdown across the repository.' },
    { kind: 'obligations', title: 'Obligations', description: 'Completion and overdue counts.' },
    { kind: 'renewals', title: 'Renewals', description: 'Upcoming and completed renewals.' },
    { kind: 'compliance', title: 'Compliance', description: 'Risk and compliance distribution.' },
  ];

  ngOnInit() {
    this.svc.contractsSummary().subscribe(s => this.summaries['contracts'] = s);
    this.svc.obligationsSummary().subscribe(s => this.summaries['obligations'] = s);
    this.svc.renewalsSummary().subscribe(s => this.summaries['renewals'] = s);
    this.svc.complianceSummary().subscribe(s => this.summaries['compliance'] = s);
  }

  objectEntries(o: any): [string, any][] {
    return o && typeof o === 'object' ? Object.entries(o).filter(([, v]) => typeof v !== 'object') : [];
  }

  download(kind: string, fmt: 'excel' | 'pdf') {
    this.svc.export(kind, fmt).subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contractiq_${kind}_report.${fmt === 'excel' ? 'xlsx' : 'pdf'}`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }
}
