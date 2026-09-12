import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import {
  Compliance as ComplianceService,
  Compliance as ComplianceRecord
} from '../../services/compliance';

@Component({
  selector: 'app-compliance',
  standalone: true,
  imports: [],
  templateUrl: './compliance.html',
  styleUrl: './compliance.css'
})
export class Compliance implements OnInit {

  complianceRecords: ComplianceRecord[] = [];

  loading = false;
  errorMessage = '';

  constructor(
    private complianceService: ComplianceService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadCompliance();
  }

  loadCompliance(): void {
    this.loading = true;
    this.errorMessage = '';

    this.cdr.detectChanges();

    this.complianceService.getCompliance().subscribe({
      next: (data) => {
        console.log('Compliance data received:', data);
        console.log('Compliance count:', data.length);

        this.complianceRecords = data;
        this.loading = false;

        this.cdr.detectChanges();
      },

      error: (error) => {
        console.error('Compliance API error:', error);

        this.loading = false;

        if (error.status === 401) {
          this.errorMessage = 'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.errorMessage = 'You do not have permission to view compliance information.';
        } else {
          this.errorMessage = 'Unable to load compliance information.';
        }

        this.cdr.detectChanges();
      }
    });
  }
}