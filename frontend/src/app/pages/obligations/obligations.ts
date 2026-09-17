import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';

interface Obligation {
  id: number;
  contract_id: number;
  title: string;
  description: string | null;
  obligation_type: string;
  due_date: string;
  assigned_to: number;
  status: string;
  completion_date: string | null;
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-obligations',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './obligations.html',
  styleUrl: './obligations.scss',
})
export class Obligations implements OnInit {
  private http = inject(HttpClient);
  private auth = inject(AuthService);

  obligations = signal<Obligation[]>([]);
  loading = signal(false);
  error = '';

  private readonly baseUrl = 'http://127.0.0.1:8000';

  ngOnInit(): void {
    this.loadObligations();
  }

  private headers(): HttpHeaders {
    const token = this.auth.getToken();

    let headers = new HttpHeaders({
      Accept: 'application/json'
    });

    if (token) {
      headers = headers.set(
        'Authorization',
        `Bearer ${token}`
      );
    }

    return headers;
  }

  loadObligations(): void {
    console.log('OBLIGATIONS: loading...');

    const token = this.auth.getToken();

    if (!token) {
      console.error('OBLIGATIONS: no authentication token');
      this.error = 'Please sign in again.';
      this.obligations.set([]);
      return;
    }

    this.loading.set(true);
    this.error = '';

    this.http.get<Obligation[]>(
      `${this.baseUrl}/obligations`,
      {
        headers: this.headers()
      }
    ).subscribe({
      next: (data) => {
        console.log(
          'OBLIGATIONS: API SUCCESS',
          data
        );

        this.obligations.set(
          Array.isArray(data) ? data : []
        );

        this.loading.set(false);
      },

      error: (err) => {
        console.error(
          'OBLIGATIONS: API ERROR',
          err
        );

        this.loading.set(false);

        if (err.status === 401) {
          this.error = 'Your session has expired. Please sign in again.';
        } else if (err.status === 403) {
          this.error = 'You do not have permission to view obligations.';
        } else if (err.status === 404) {
          this.error = 'Obligations endpoint not found.';
        } else if (err.status === 0) {
          this.error =
            'Unable to connect to the backend. Make sure FastAPI is running on port 8000.';
        } else {
          this.error =
            err.error?.detail ||
            'Unable to load obligations.';
        }
      }
    });
  }

  getStatusClass(status: string): string {
    return status
      .toLowerCase()
      .replace(/\s+/g, '-');
  }
}
