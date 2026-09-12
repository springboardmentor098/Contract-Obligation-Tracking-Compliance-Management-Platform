import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Renewals as RenewalsService, Renewal } from '../../services/renewals';

@Component({
  selector: 'app-renewals',
  standalone: true,
  imports: [],
  templateUrl: './renewals.html',
  styleUrl: './renewals.css'
})
export class Renewals implements OnInit {

  renewals: Renewal[] = [];

  loading = false;
  errorMessage = '';

  constructor(
    private renewalsService: RenewalsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadRenewals();
  }

  loadRenewals(): void {
    this.loading = true;
    this.errorMessage = '';

    this.cdr.detectChanges();

    this.renewalsService.getRenewals().subscribe({
      next: (data) => {
        console.log('Renewals data received:', data);
        console.log('Renewals count:', data.length);

        this.renewals = data;
        this.loading = false;

        this.cdr.detectChanges();
      },

      error: (error) => {
        console.error('Renewals API error:', error);

        this.loading = false;

        if (error.status === 401) {
          this.errorMessage = 'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.errorMessage = 'You do not have permission to view renewals.';
        } else {
          this.errorMessage = 'Unable to load renewals.';
        }

        this.cdr.detectChanges();
      }
    });
  }
}