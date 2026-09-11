import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api } from '../../services/api';

interface Renewal {
  id: number;
  contract_id: number;
  renewal_date: string | null;
  previous_expiry_date: string;
  new_expiry_date: string | null;
  status: string;
  assigned_to: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-renewals',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './renewals.html',
  styleUrl: './renewals.scss',
})
export class Renewals implements OnInit {
  private api = inject(Api);

  renewals = signal<Renewal[]>([]);
  loading = signal(false);
  error = '';

  ngOnInit(): void {
    this.loadRenewals();
  }

  loadRenewals(): void {
    console.log('RENEWALS: loading...');

    this.loading.set(true);
    this.error = '';

    this.api.getRenewals().subscribe({
      next: (data: Renewal[]) => {
        console.log('RENEWALS: API SUCCESS', data);
        console.log('RENEWALS: COUNT', data.length);

        this.renewals.set(data);
        this.loading.set(false);
      },

      error: (err) => {
        console.error('RENEWALS: API ERROR', err);

        this.error =
          err?.error?.detail ||
          'Failed to load renewals.';

        this.loading.set(false);
      }
    });
  }

  updateStatus(
    renewalId: number,
    newStatus: string
  ): void {
    this.error = '';

    this.api.updateRenewalStatus(
      renewalId,
      newStatus
    ).subscribe({
      next: (updated: Renewal) => {
        this.renewals.update(items =>
          items.map(item =>
            item.id === updated.id ? updated : item
          )
        );
      },

      error: (err) => {
        console.error('RENEWALS: STATUS ERROR', err);

        this.error =
          err?.error?.detail ||
          'Failed to update renewal status.';
      }
    });
  }

  completeRenewal(renewalId: number): void {
    this.error = '';

    if (
      !confirm(
        'Complete this renewal? This will update the contract expiry date.'
      )
    ) {
      return;
    }

    this.api.completeRenewal(
      renewalId
    ).subscribe({
      next: (updated: Renewal) => {
        this.renewals.update(items =>
          items.map(item =>
            item.id === updated.id ? updated : item
          )
        );
      },

      error: (err) => {
        console.error('RENEWALS: COMPLETE ERROR', err);

        this.error =
          err?.error?.detail ||
          'Failed to complete renewal.';
      }
    });
  }

  formatDate(value: string | null): string {
    if (!value) {
      return '—';
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }
}
