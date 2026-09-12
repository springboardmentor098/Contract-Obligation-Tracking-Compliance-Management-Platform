import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Obligations as ObligationsService, Obligation } from '../../services/obligations';

@Component({
  selector: 'app-obligations',
  standalone: true,
  imports: [],
  templateUrl: './obligations.html',
  styleUrl: './obligations.css'
})
export class Obligations implements OnInit {

  obligations: Obligation[] = [];

  loading = false;
  errorMessage = '';

  constructor(
    private obligationsService: ObligationsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadObligations();
  }

  loadObligations(): void {
    this.loading = true;
    this.errorMessage = '';

    this.cdr.detectChanges();

    this.obligationsService.getObligations().subscribe({
      next: (data) => {
        console.log('Obligations data received:', data);
        console.log('Obligations count:', data.length);

        this.obligations = data;
        this.loading = false;

        this.cdr.detectChanges();
      },

      error: (error) => {
        console.error('Obligations API error:', error);

        this.loading = false;

        if (error.status === 401) {
          this.errorMessage = 'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.errorMessage = 'You do not have permission to view obligations.';
        } else {
          this.errorMessage = 'Unable to load obligations.';
        }

        this.cdr.detectChanges();
      }
    });
  }
}