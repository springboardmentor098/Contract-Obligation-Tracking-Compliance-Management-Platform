import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { RenewalsService } from '../../core/data.service';
import { Renewal } from '../../core/models';

@Component({
  selector: 'app-renewal-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="page-head">
    <div>
      <h1>Renewals</h1>
      <p class="muted">{{ renewals().length }} renewal records</p>
    </div>
  </div>

  <p class="error-banner" *ngIf="error()">{{ error() }}</p>

  <div class="panel" *ngIf="renewals().length; else empty">
    <table class="ledger">
      <thead><tr><th>Contract</th><th>Renewal date</th><th>Previous expiry</th><th>New expiry</th><th>Status</th><th></th></tr></thead>
      <tbody>
        <tr *ngFor="let r of renewals()">
          <td><a [routerLink]="['/contracts', r.contract_id]" class="docket-num">#{{ r.contract_id }}</a></td>
          <td>{{ r.renewal_date | date:'mediumDate' }}</td>
          <td>{{ r.previous_expiry_date | date:'mediumDate' }}</td>
          <td>{{ r.new_expiry_date | date:'mediumDate' }}</td>
          <td><span class="tag" [ngClass]="tag(r.status)">{{ r.status }}</span></td>
          <td><button class="btn-ghost btn-sm" *ngIf="r.status === 'In Progress'" (click)="renew(r)">Mark renewed</button></td>
        </tr>
      </tbody>
    </table>
  </div>
  <ng-template #empty>
    <div class="panel empty-state">
      <strong>No renewal activity yet</strong>
      Renewal records appear here as contracts approach their expiry dates.
    </div>
  </ng-template>
  `,
  styles: [`.page-head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; }`],
})
export class RenewalListComponent implements OnInit {
  private svc = inject(RenewalsService);
  renewals = signal<Renewal[]>([]);
  error = signal('');

  ngOnInit() {
    this.svc.list().subscribe({
      next: list => this.renewals.set(list),
      error: () => this.error.set('Unable to load renewals.'),
    });
  }

  tag(status: string): string {
    if (status === 'Renewed') return 'tag-seal';
    if (status === 'Upcoming' || status === 'In Progress') return 'tag-amber';
    if (status === 'Expired') return 'tag-rose';
    return 'tag-slate';
  }

  renew(r: Renewal) {
    this.svc.renew(r.id).subscribe({
      next: updated => this.renewals.set(this.renewals().map(x => x.id === updated.id ? updated : x)),
      error: () => this.error.set('Unable to complete that renewal.'),
    });
  }
}
