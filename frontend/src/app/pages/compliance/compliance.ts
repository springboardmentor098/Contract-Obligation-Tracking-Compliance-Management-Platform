import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { forkJoin } from 'rxjs';
import { Api } from '../../services/api';

@Component({
  selector: 'app-compliance',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './compliance.html',
  styleUrl: './compliance.scss',
})
export class Compliance implements OnInit {
  private api = inject(Api);
  private cdr = inject(ChangeDetectorRef);

  loading = false;
  error = '';

  summary: any = null;
  risks: any[] = [];

  ngOnInit(): void {
    this.loadCompliance();
  }

  loadCompliance(): void {

    this.loading = true;
    this.error = '';

    forkJoin({
      summary: this.api.getComplianceSummary(),
      risks: this.api.getRiskReport(),
    }).subscribe({
      next: (data) => {

        this.summary = data.summary;
        this.risks = Array.isArray(data.risks) ? data.risks : [];


        this.loading = false;
        this.cdr.detectChanges();

      },

      error: (err) => {

        this.loading = false;
        this.cdr.detectChanges();

        if (err?.status === 401) {
          this.error = 'Your session has expired. Please sign in again.';
        } else if (err?.status === 403) {
          this.error = 'You do not have permission to view compliance data.';
        } else {
          this.error =
            'Unable to load compliance data. Please check the backend connection and try again.';
        }
      },

      complete: () => {
      },
    });
  }

  getScoreClass(): string {
    const score = Number(this.summary?.average_score ?? 0);

    if (score >= 80) {
      return 'good';
    }

    if (score >= 50) {
      return 'warning';
    }

    return 'danger';
  }
}
