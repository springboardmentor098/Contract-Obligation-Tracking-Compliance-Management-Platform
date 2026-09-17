import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';

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
  selector: 'app-renewal-monitoring',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './renewal-monitoring.html',
  styleUrl: './renewal-monitoring.scss',
})
export class RenewalMonitoring implements OnInit {
  private http = inject(HttpClient);

  upcoming = signal<Renewal[]>([]);
  expired = signal<Renewal[]>([]);
  loading = signal(false);
  error = '';

  days = 365;

  ngOnInit(): void {
    this.loadMonitoring();
  }

  private headers(): HttpHeaders {
    const token = localStorage.getItem('access_token');

    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    });
  }

  loadMonitoring(): void {
    this.loading.set(true);
    this.error = '';

    Promise.all([
      this.http.get<Renewal[]>(
        `http://127.0.0.1:8000/renewals/monitoring/upcoming?days=${this.days}`,
        { headers: this.headers() }
      ).toPromise(),

      this.http.get<Renewal[]>(
        'http://127.0.0.1:8000/renewals/monitoring/expired',
        { headers: this.headers() }
      ).toPromise()
    ])
    .then(([upcoming, expired]) => {
      this.upcoming.set(upcoming ?? []);
      this.expired.set(expired ?? []);
      this.loading.set(false);
    })
    .catch((err) => {
      console.error('RENEWAL MONITORING ERROR:', err);

      this.error =
        err?.error?.detail ||
        'Unable to load renewal monitoring data.';

      this.loading.set(false);
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
