import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
  ComplianceRecord,
  ComplianceSummary,
  HighRiskContract,
  NonCompliantContract,
  ComplianceService
} from '../../services/compliance.service';

@Component({
  selector: 'app-compliance',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatTableModule,
    MatTooltipModule
  ],
  templateUrl: './compliance.component.html',
  styleUrl: './compliance.component.scss'
})
export class ComplianceComponent implements OnInit {

  private readonly complianceService =
    inject(ComplianceService);

  complianceRecords: ComplianceRecord[] = [];
  nonCompliantContracts: NonCompliantContract[] = [];
  highRiskContracts: HighRiskContract[] = [];

  summary: ComplianceSummary | null = null;

  loading = true;
  error = '';

  displayedColumns: string[] = [
    'contract_id',
    'contract_number',
    'compliance_status',
    'compliance_score',
    'total_obligations',
    'completed_obligations',
    'pending_obligations',
    'overdue_obligations',
    'risk_level'
  ];

  ngOnInit(): void {
    this.loadCompliance();
  }

  loadCompliance(): void {
    this.loading = true;
    this.error = '';

    this.complianceService.getAllCompliance().subscribe({
      next: (records) => {
        this.complianceRecords = records;
        this.loading = false;
      },
      error: (error) => {
        console.error(
          'Compliance records API error:',
          error
        );

        this.loading = false;
        this.error = this.getErrorMessage(
          error,
          'Unable to load compliance information.'
        );
      }
    });

    this.complianceService.getSummary().subscribe({
      next: (summary) => {
        this.summary = summary;
      },
      error: (error) => {
        console.error(
          'Compliance summary API error:',
          error
        );
      }
    });

    this.complianceService
      .getNonCompliantContracts()
      .subscribe({
        next: (contracts) => {
          this.nonCompliantContracts = contracts;
        },
        error: (error) => {
          console.error(
            'Non-compliant contracts API error:',
            error
          );
        }
      });

    this.complianceService
      .getHighRiskContracts()
      .subscribe({
        next: (contracts) => {
          this.highRiskContracts = contracts;
        },
        error: (error) => {
          console.error(
            'High-risk contracts API error:',
            error
          );
        }
      });
  }

  retry(): void {
    this.loadCompliance();
  }

  getStatusClass(
    status: string | null
  ): string {

    if (!status) {
      return 'unknown';
    }

    return status
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  getRiskClass(
    risk: string | null
  ): string {

    if (!risk) {
      return 'unknown';
    }

    return risk
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  formatScore(
    score: number | null
  ): string {

    if (score === null || score === undefined) {
      return '—';
    }

    return `${score}%`;
  }

  formatValue(
    value: number | null | undefined
  ): string {

    if (
      value === null ||
      value === undefined
    ) {
      return '0';
    }

    return value.toString();
  }

  private getErrorMessage(
    error: any,
    fallback: string
  ): string {

    if (error?.status === 401) {
      return 'Your session has expired. Please log in again.';
    }

    if (error?.status === 403) {
      return 'You do not have permission to view compliance information.';
    }

    if (error?.status === 404) {
      return 'Compliance endpoint was not found on the backend.';
    }

    if (error?.status === 0) {
      return 'Unable to connect to the backend. Please make sure FastAPI is running.';
    }

    return (
      error?.error?.detail ||
      fallback
    );
  }
}