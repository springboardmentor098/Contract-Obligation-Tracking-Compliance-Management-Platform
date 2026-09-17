import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatSelectModule } from '@angular/material/select';

import {
  ComplianceService,
  ComplianceRecord,
  ComplianceSummary
} from '../services/compliance';

@Component({
  selector: 'app-compliance',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatTableModule,
    MatSelectModule
  ],
  templateUrl: './compliance.html',
  styleUrl: './compliance.css'
})
export class Compliance implements OnInit {

  records: ComplianceRecord[] = [];
  filteredRecords: ComplianceRecord[] = [];

  summary: ComplianceSummary | null = null;

  loading = false;

  errorMessage = '';
  successMessage = '';

  searchText = '';
  selectedStatus = '';
  selectedRisk = '';

  selectedRecord: ComplianceRecord | null = null;
  history: any[] = [];
  historyLoading = false;

  displayedColumns = [
    'contract_number',
    'compliance_status',
    'compliance_score',
    'total_obligations',
    'completed_obligations',
    'pending_obligations',
    'overdue_obligations',
    'risk_level',
    'actions'
  ];

  statuses = [
    'Compliant',
    'Pending',
    'Delayed',
    'Non-Compliant',
    'High Risk'
  ];

  riskLevels = [
    'Low',
    'Medium',
    'High'
  ];

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

    this.complianceService.getComplianceRecords().subscribe({
      next: (data) => {
        this.records = data;
        this.applyFilters();
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Compliance API error:', error);
        this.errorMessage = 'Unable to load compliance records.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });

    this.complianceService.getComplianceSummary().subscribe({
      next: (data) => {
        this.summary = data;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Compliance summary API error:', error);
      }
    });
  }

  applyFilters(): void {
    const search = this.searchText.toLowerCase().trim();

    this.filteredRecords = this.records.filter(record => {

      const matchesSearch =
        !search ||
        record.contract_number.toLowerCase().includes(search) ||
        String(record.contract_id).includes(search);

      const matchesStatus =
        !this.selectedStatus ||
        record.compliance_status === this.selectedStatus;

      const matchesRisk =
        !this.selectedRisk ||
        record.risk_level === this.selectedRisk;

      return matchesSearch && matchesStatus && matchesRisk;
    });
  }

  clearFilters(): void {
    this.searchText = '';
    this.selectedStatus = '';
    this.selectedRisk = '';
    this.applyFilters();
  }

  viewDetails(record: ComplianceRecord): void {
    this.selectedRecord = record;
    this.history = [];
    this.historyLoading = true;
    this.errorMessage = '';

    this.complianceService
      .getComplianceHistory(record.contract_id)
      .subscribe({
        next: (data) => {
          this.history = data;
          this.historyLoading = false;
          this.cdr.markForCheck();
        },
        error: (error) => {
          console.error('Compliance history error:', error);
          this.historyLoading = false;
          this.errorMessage =
            'Unable to load compliance history.';
          this.cdr.markForCheck();
        }
      });
  }

  closeDetails(): void {
    this.selectedRecord = null;
    this.history = [];
  }

  getScoreClass(score: number): string {
    if (score >= 80) {
      return 'score-good';
    }

    if (score >= 50) {
      return 'score-medium';
    }

    return 'score-low';
  }

  getStatusClass(status: string): string {
    return status
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  getRiskClass(risk: string): string {
    return risk.toLowerCase();
  }
}
