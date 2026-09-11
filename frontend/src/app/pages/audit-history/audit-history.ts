import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface AuditLog {
  id: number;
  user_id: number;
  entity_type: string | null;
  entity_id: number | null;
  action: string;
  old_values: any;
  new_values: any;
  ip_address: string | null;
  created_at: string;
}

@Component({
  selector: 'app-audit-history',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './audit-history.html',
  styleUrl: './audit-history.scss',
})
export class AuditHistory implements OnInit {
  private http = inject(HttpClient);

  auditLogs = signal<AuditLog[]>([]);
  loading = signal(false);
  error = '';

  ngOnInit(): void {
    this.loadAuditHistory();
  }

  private headers(): HttpHeaders {
    const token = localStorage.getItem('access_token');

    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    });
  }

  loadAuditHistory(): void {
    this.loading.set(true);
    this.error = '';

    this.http.get<AuditLog[]>(
      'http://127.0.0.1:8000/audit-history',
      { headers: this.headers() }
    ).subscribe({
      next: (data) => {
        this.auditLogs.set(data ?? []);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Failed to load audit history:', err);

        this.error =
          err?.error?.detail ||
          'Unable to load audit history. Please check the backend connection.';

        this.loading.set(false);
      }
    });
  }

  formatDate(value: string): string {
    if (!value) {
      return '—';
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString('en-US');
  }

  formatValues(value: any): string {
    if (value === null || value === undefined) {
      return '—';
    }

    if (typeof value === 'object') {
      return JSON.stringify(value);
    }

    return String(value);
  }
}
