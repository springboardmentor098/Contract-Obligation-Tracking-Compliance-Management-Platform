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
  ComplianceHistory,
  HighRiskContract,
  NonCompliantContract,
  ComplianceService
} from '../../services/compliance.service';

import {
  Contract,
  ContractService
} from '../../services/contract.service';

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

  private readonly contractService =
    inject(ContractService);

  complianceRecords: ComplianceRecord[] = [];
  nonCompliantContracts: NonCompliantContract[] = [];
  highRiskContracts: HighRiskContract[] = [];

  contracts: Contract[] = [];
  contractNumberMap: Record<string, string> = {};

  summary: ComplianceSummary | null = null;

  loading = true;
  error = '';

  evaluationError = '';
  evaluatingContractId: string | number | null = null;

  showHistory = false;
  historyLoading = false;
  historyError = '';

  selectedHistoryContractId: string | number | null = null;
  selectedHistoryContractNumber = '';

  complianceHistory: ComplianceHistory[] = [];

  displayedColumns: string[] = [
    'contract_id',
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

  ngOnInit(): void {
    this.loadCompliance();
    this.loadContracts();
  }

  loadCompliance(): void {
    this.loading = true;
    this.error = '';
    this.evaluationError = '';

    // Load all compliance records
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

    // Load compliance summary
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

    // Load non-compliant contracts
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

    // Load high-risk contracts
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

  loadContracts(): void {
    this.contractService.getContracts().subscribe({
      next: (contracts) => {
        this.contracts = contracts;

        this.contractNumberMap = {};

        for (const contract of contracts) {
          this.contractNumberMap[String(contract.id)] =
            contract.contract_number;
        }
      },
      error: (error) => {
        console.error(
          'Contracts API error:',
          error
        );
      }
    });
  }

  getContractNumber(
    contractId: string | number,
    contractNumber: string | null | undefined
  ): string {

    if (contractNumber) {
      return contractNumber;
    }

    return (
      this.contractNumberMap[String(contractId)] ||
      'N/A'
    );
  }

  evaluateContract(
    contractId: string | number
  ): void {

    this.evaluatingContractId = contractId;
    this.evaluationError = '';

    this.complianceService
      .evaluateContract(String(contractId))
      .subscribe({
        next: (result) => {
          console.log(
            'Compliance evaluation successful:',
            result
          );

          this.evaluatingContractId = null;

          // Refresh compliance data after evaluation
          this.loadCompliance();
        },
        error: (error) => {
          console.error(
            'Compliance evaluation API error:',
            error
          );

          this.evaluatingContractId = null;

          this.evaluationError =
            this.getErrorMessage(
              error,
              'Unable to evaluate contract compliance.'
            );
        }
      });
  }

  isEvaluating(
    contractId: string | number
  ): boolean {

    return (
      String(this.evaluatingContractId) ===
      String(contractId)
    );
  }

  viewHistory(
    contractId: string | number,
    contractNumber?: string | null
  ): void {

    this.selectedHistoryContractId = contractId;

    this.selectedHistoryContractNumber =
      this.getContractNumber(
        contractId,
        contractNumber
      );

    this.showHistory = true;
    this.historyLoading = true;
    this.historyError = '';
    this.complianceHistory = [];

    this.complianceService
      .getComplianceHistory(String(contractId))
      .subscribe({
        next: (history) => {
          this.complianceHistory = history;
          this.historyLoading = false;
        },
        error: (error) => {
          console.error(
            'Compliance history API error:',
            error
          );

          this.historyLoading = false;

          this.historyError =
            this.getErrorMessage(
              error,
              'Unable to load compliance history.'
            );
        }
      });
  }

  closeHistory(): void {
    this.showHistory = false;

    this.selectedHistoryContractId = null;

    this.selectedHistoryContractNumber = '';

    this.complianceHistory = [];

    this.historyError = '';
  }

  retry(): void {
    this.loadCompliance();
    this.loadContracts();
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

    if (
      score === null ||
      score === undefined
    ) {
      return 'N/A';
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

  formatDateTime(
    value: string | null | undefined
  ): string {

    if (!value) {
      return 'N/A';
    }

    const date = new Date(value);

    if (isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString();
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