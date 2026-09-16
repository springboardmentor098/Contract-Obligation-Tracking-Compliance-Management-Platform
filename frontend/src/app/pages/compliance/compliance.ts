import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import {
  ComplianceData,
  ComplianceService
} from '../../core/services/compliance.service';

@Component({
  selector: 'app-compliance',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './compliance.html',
  styleUrl: './compliance.scss'
})
export class Compliance implements OnInit {
  private readonly complianceService = inject(ComplianceService);
  private readonly cdr = inject(ChangeDetectorRef);

  data: ComplianceData | null = null;
  loading = true;
  error = '';

  ngOnInit(): void {
    this.loadCompliance();
  }

  loadCompliance(): void {
    this.loading = true;
    this.error = '';

    this.complianceService.getCompliance().subscribe({
      next: (response) => {
        this.data = response.compliance;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Compliance loading error:', err);
        this.error = 'Unable to load compliance data.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  getComplianceClass(): string {
    if (!this.data) return '';

    if (this.data.compliance_rate >= 80) {
      return 'good';
    }

    if (this.data.compliance_rate >= 60) {
      return 'warning';
    }

    return 'danger';
  }

  getRiskLevel(): string {
    if (!this.data) return '';

    if (this.data.high_risk_contracts === 0) {
      return 'Low Risk';
    }

    if (this.data.high_risk_contracts <= 2) {
      return 'Moderate Risk';
    }

    return 'High Risk';
  }
}
