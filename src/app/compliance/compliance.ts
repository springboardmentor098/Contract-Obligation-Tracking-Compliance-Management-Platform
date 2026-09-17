import { CommonModule } from '@angular/common';

import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';

import { FormsModule } from '@angular/forms';

import {
  HttpErrorResponse
} from '@angular/common/http';

import {
  ActivatedRoute
} from '@angular/router';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { ComplianceService } from '../services/compliance.service';

import {
  ComplianceEvaluation,
  ComplianceRecord
} from '../models/compliance.model';

@Component({
  selector: 'app-compliance',
  standalone: true,

  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],

  templateUrl: './compliance.html',
  styleUrls: ['./compliance.css']
})
export class Compliance implements OnInit {

  evaluations: ComplianceEvaluation[] = [];

  filteredEvaluations:
    ComplianceEvaluation[] = [];

  savedRecords:
    ComplianceRecord[] = [];

  contractHistory:
    ComplianceRecord[] = [];

  selectedRecord:
    ComplianceRecord | null = null;

  selectedEvaluation:
    ComplianceEvaluation | null = null;

  selectedContractId:
    number | null = null;

  contractIdInput:
    string | number = '';

  evaluationNotes = '';

  searchText = '';

  statusFilter = 'ALL';

  riskFilter = 'ALL';

  statusOptions: string[] = [
    'Compliant',
    'Pending',
    'Delayed',
    'Non-Compliant'
  ];

  riskOptions: string[] = [
    'Low',
    'Medium',
    'High'
  ];

  loading = false;

  actionLoading = false;

  successMessage = '';

  errorMessage = '';

  compliantCount = 0;

  nonCompliantCount = 0;

  highRiskCount = 0;

  /*
   * Contract ID received from Notifications page.
   */
  private requestedContractId:
    number | null = null;

  constructor(
    private readonly complianceService: ComplianceService,

    private readonly route: ActivatedRoute,

    private readonly cdr: ChangeDetectorRef
  ) {}

  // =========================================================
  // INITIALIZE
  // =========================================================

  ngOnInit(): void {

    const contractIdParam =
      this.route.snapshot
        .queryParamMap
        .get('contractId');

    const contractId =
      Number(contractIdParam);

    if (
      Number.isInteger(contractId) &&
      contractId > 0
    ) {

      this.requestedContractId =
        contractId;

      this.contractIdInput =
        contractId;

      console.log(
        `Compliance page opened for Contract #${contractId}`
      );
    }

    this.loadCompliance();

    this.loadSavedRecords();
  }

  // =========================================================
  // LOAD COMPLIANCE
  // =========================================================

  loadCompliance(): void {

    this.loading = true;

    this.errorMessage = '';

    this.complianceService
      .getAllCompliance()
      .subscribe({

        next: (
          data: ComplianceEvaluation[]
        ) => {

          this.evaluations =
            data ?? [];

          this.updateCounts();

          this.applyFilters();

          this.loading = false;

          this.cdr.detectChanges();

          /*
           * Automatically open the contract
           * requested by a notification.
           */

          if (
            this.requestedContractId
          ) {

            const contractId =
              this.requestedContractId;

            setTimeout(() => {

              this.openRequestedContract(
                contractId
              );

            }, 0);
          }
        },

        error: (
          error: HttpErrorResponse
        ) => {

          this.loading = false;

          this.handleError(
            error,
            'Failed to load compliance data.'
          );

          this.cdr.detectChanges();
        }

      });
  }

  // =========================================================
  // LOAD SAVED RECORDS
  // =========================================================

  loadSavedRecords(): void {

    this.complianceService
      .getSavedRecords()
      .subscribe({

        next: (
          data: ComplianceRecord[]
        ) => {

          this.savedRecords =
            data ?? [];

          this.cdr.detectChanges();
        },

        error: (
          error: HttpErrorResponse
        ) => {

          this.handleError(
            error,
            'Failed to load saved compliance records.'
          );

          this.cdr.detectChanges();
        }

      });
  }

  // =========================================================
  // OPEN REQUESTED CONTRACT
  // =========================================================

  private openRequestedContract(
    contractId: number
  ): void {

    console.log(
      `Looking for compliance record for Contract #${contractId}`
    );

    const evaluation =
      this.evaluations.find(
        (item: ComplianceEvaluation) =>
          this.getContractId(item) === contractId
      );

    /*
     * Existing compliance evaluation found.
     */

    if (evaluation) {

      this.searchText =
        String(contractId);

      this.applyFilters();

      this.viewEvaluation(
        evaluation
      );

      this.successMessage =
        `Contract #${contractId} compliance details opened.`;

      this.cdr.detectChanges();

      setTimeout(() => {

        const detailsElement =
          document.querySelector(
            '.details-card'
          );

        detailsElement?.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });

      }, 100);

      return;
    }

    /*
     * No evaluation in the main list.
     * Ask backend directly for the contract.
     */

    console.log(
      `No list record found. Loading Contract #${contractId} directly.`
    );

    this.contractIdInput =
      contractId;

    this.getComplianceForNotification(
      contractId
    );
  }

  // =========================================================
  // GET CONTRACT COMPLIANCE FOR NOTIFICATION
  // =========================================================

  private getComplianceForNotification(
    contractId: number
  ): void {

    this.actionLoading = true;

    this.errorMessage = '';

    this.complianceService
      .getContractCompliance(contractId)
      .subscribe({

        next: (
          evaluation: ComplianceEvaluation
        ) => {

          this.selectedContractId =
            contractId;

          this.selectedEvaluation =
            evaluation;

          this.selectedRecord =
            null;

          this.contractIdInput =
            contractId;

          this.evaluationNotes =
            String(
              (evaluation as any)?.notes ??
              `Compliance evaluation for contract ${contractId}`
            );

          this.actionLoading = false;

          this.successMessage =
            `Contract #${contractId} compliance details opened.`;

          this.cdr.detectChanges();

          setTimeout(() => {

            const detailsElement =
              document.querySelector(
                '.details-card'
              );

            detailsElement?.scrollIntoView({
              behavior: 'smooth',
              block: 'start'
            });

          }, 100);
        },

        error: (
          error: HttpErrorResponse
        ) => {

          this.actionLoading = false;

          this.handleError(
            error,
            `Unable to load compliance for contract #${contractId}.`
          );

          this.cdr.detectChanges();
        }

      });
  }

  // =========================================================
  // UPDATE COUNTS
  // =========================================================

  private updateCounts(): void {

    this.compliantCount =
      this.evaluations.filter(
        (
          evaluation: ComplianceEvaluation
        ) =>
          this.getStatus(
            evaluation
          ).toLowerCase() === 'compliant'
      ).length;

    this.nonCompliantCount =
      this.evaluations.filter(
        (
          evaluation: ComplianceEvaluation
        ) =>
          this.getStatus(
            evaluation
          ).toLowerCase() === 'non-compliant'
      ).length;

    this.highRiskCount =
      this.evaluations.filter(
        (
          evaluation: ComplianceEvaluation
        ) =>
          this.getRisk(
            evaluation
          ).toLowerCase() === 'high'
      ).length;
  }

  // =========================================================
  // TOTAL CONTRACTS
  // =========================================================

  getTotalContracts(): number {

    return this.evaluations.length;
  }

  // =========================================================
  // SEARCH
  // =========================================================

  onSearchChange(
    value?: string
  ): void {

    if (
      value !== undefined
    ) {

      this.searchText =
        value;
    }

    this.applyFilters();
  }

  // =========================================================
  // STATUS FILTER
  // =========================================================

  onStatusFilterChange(
    value?: string
  ): void {

    if (
      value !== undefined
    ) {

      this.statusFilter =
        value;
    }

    this.applyFilters();
  }

  // =========================================================
  // RISK FILTER
  // =========================================================

  onRiskFilterChange(
    value?: string
  ): void {

    if (
      value !== undefined
    ) {

      this.riskFilter =
        value;
    }

    this.applyFilters();
  }

  // =========================================================
  // APPLY FILTERS
  // =========================================================

  applyFilters(): void {

    const search =
      String(
        this.searchText ?? ''
      )
        .trim()
        .toLowerCase();

    this.filteredEvaluations =
      this.evaluations.filter(
        (
          evaluation: ComplianceEvaluation
        ) => {

          const contractId =
            this.getContractId(
              evaluation
            );

          const status =
            this.getStatus(
              evaluation
            );

          const risk =
            this.getRisk(
              evaluation
            );

          const matchesSearch =
            search === '' ||
            String(
              contractId
            ).includes(search);

          const matchesStatus =
            this.statusFilter === 'ALL' ||
            status ===
              this.statusFilter;

          const matchesRisk =
            this.riskFilter === 'ALL' ||
            risk ===
              this.riskFilter;

          return (
            matchesSearch &&
            matchesStatus &&
            matchesRisk
          );
        }
      );
  }

  // =========================================================
  // EVALUATE CONTRACT
  // =========================================================

  evaluateContract(): void {

    this.successMessage = '';

    this.errorMessage = '';

    const input =
      String(
        this.contractIdInput ?? ''
      ).trim();

    const contractId =
      Number(input);

    if (
      input === '' ||
      !/^\d+$/.test(input) ||
      !Number.isInteger(contractId) ||
      contractId <= 0
    ) {

      this.errorMessage =
        'Please enter a valid contract ID.';

      return;
    }

    this.actionLoading = true;

    this.complianceService
      .getContractCompliance(
        contractId
      )
      .subscribe({

        next: (
          evaluation: ComplianceEvaluation
        ) => {

          this.selectedContractId =
            contractId;

          this.selectedEvaluation =
            evaluation;

          this.selectedRecord =
            null;

          this.evaluationNotes =
            String(
              (evaluation as any)?.notes ??
              `Compliance evaluation for contract ${contractId}`
            );

          this.actionLoading = false;

          this.successMessage =
            `Contract #${contractId} compliance details loaded.`;

          this.cdr.detectChanges();
        },

        error: (
          error: HttpErrorResponse
        ) => {

          this.actionLoading = false;

          this.handleError(
            error,
            `Unable to load compliance for contract #${contractId}.`
          );

          this.cdr.detectChanges();
        }

      });
  }

  // =========================================================
  // GET CONTRACT COMPLIANCE
  // =========================================================

  getContractCompliance(): void {

    this.evaluateContract();
  }

  // =========================================================
  // SAVE EVALUATION
  // =========================================================

  saveEvaluation(): void {

    this.successMessage = '';

    this.errorMessage = '';

    const input =
      String(
        this.contractIdInput ?? ''
      ).trim();

    const contractId =
      Number(input);

    if (
      input === '' ||
      !/^\d+$/.test(input) ||
      !Number.isInteger(contractId) ||
      contractId <= 0
    ) {

      this.errorMessage =
        'Please enter a valid contract ID.';

      return;
    }

    this.actionLoading = true;

    const notes =
      String(
        this.evaluationNotes ?? ''
      ).trim() ||
      `Compliance evaluation for contract ${contractId}`;

    this.complianceService
      .createEvaluation(
        contractId,
        notes
      )
      .subscribe({

        next: (
          record: ComplianceRecord
        ) => {

          this.actionLoading = false;

          this.selectedContractId =
            contractId;

          this.selectedRecord =
            record;

          this.selectedEvaluation =
            null;

          this.successMessage =
            `Compliance evaluation for contract #${contractId} completed successfully.`;

          this.loadCompliance();

          this.loadSavedRecords();

          this.cdr.detectChanges();
        },

        error: (
          error: HttpErrorResponse
        ) => {

          this.actionLoading = false;

          this.handleError(
            error,
            `Compliance evaluation failed for contract #${contractId}.`
          );

          this.cdr.detectChanges();
        }

      });
  }

  // =========================================================
  // VIEW EVALUATION
  // =========================================================

  viewEvaluation(
    evaluation: ComplianceEvaluation
  ): void {

    this.selectedEvaluation =
      evaluation;

    this.selectedRecord =
      null;

    this.selectedContractId =
      this.getContractId(
        evaluation
      );

    this.contractIdInput =
      this.selectedContractId;

    this.evaluationNotes =
      String(
        (evaluation as any)?.notes ??
        ''
      );

    this.cdr.detectChanges();
  }

  // =========================================================
  // VIEW RECORD
  // =========================================================

  viewRecord(
    record: ComplianceRecord
  ): void {

    this.selectedRecord =
      record;

    this.selectedEvaluation =
      null;

    this.selectedContractId =
      Number(
        (record as any)?.contract_id ??
        0
      );

    if (
      this.selectedContractId > 0
    ) {

      this.contractIdInput =
        this.selectedContractId;
    }

    this.cdr.detectChanges();
  }

  // =========================================================
  // CONTRACT HISTORY
  // =========================================================

  loadContractHistory(
    contractId?: number
  ): void {

    const id =
      contractId ??
      Number(
        String(
          this.contractIdInput ?? ''
        ).trim()
      );

    if (
      !Number.isInteger(id) ||
      id <= 0
    ) {

      this.errorMessage =
        'Please enter a valid contract ID.';

      return;
    }

    this.actionLoading = true;

    this.errorMessage = '';

    this.complianceService
      .getContractHistory(id)
      .subscribe({

        next: (
          data: ComplianceRecord[]
        ) => {

          this.contractHistory =
            data ?? [];

          this.selectedContractId =
            id;

          this.contractIdInput =
            id;

          this.actionLoading = false;

          this.cdr.detectChanges();
        },

        error: (
          error: HttpErrorResponse
        ) => {

          this.actionLoading = false;

          this.handleError(
            error,
            `Failed to load compliance history for contract #${id}.`
          );

          this.cdr.detectChanges();
        }

      });
  }

  // =========================================================
  // CLEAR SELECTION
  // =========================================================

  clearSelection(): void {

    this.selectedRecord =
      null;

    this.selectedEvaluation =
      null;

    this.selectedContractId =
      null;

    this.contractHistory =
      [];

    this.successMessage =
      '';

    this.errorMessage =
      '';

    this.cdr.detectChanges();
  }

  // =========================================================
  // GET CONTRACT ID
  // =========================================================

  private getContractId(
    evaluation: ComplianceEvaluation
  ): number {

    return Number(
      (evaluation as any)?.contract_id ??
      (evaluation as any)?.id ??
      0
    );
  }

  // =========================================================
  // GET STATUS
  // =========================================================

  private getStatus(
    evaluation: ComplianceEvaluation
  ): string {

    return String(
      (evaluation as any)?.status ??
      (evaluation as any)?.compliance_status ??
      ''
    );
  }

  // =========================================================
  // GET RISK
  // =========================================================

  private getRisk(
    evaluation: ComplianceEvaluation
  ): string {

    return String(
      (evaluation as any)?.risk_level ??
      ''
    );
  }

  // =========================================================
  // STATUS CLASS
  // =========================================================

  getStatusClass(
    status: string | undefined
  ): string {

    switch (
      String(
        status ?? ''
      ).toLowerCase()
    ) {

      case 'compliant':
        return 'status-compliant';

      case 'pending':
        return 'status-pending';

      case 'delayed':
        return 'status-delayed';

      case 'non-compliant':
        return 'status-non-compliant';

      default:
        return '';
    }
  }

  // =========================================================
  // SCORE CLASS
  // =========================================================

  getScoreClass(
    score: number | undefined
  ): string {

    const value =
      Number(
        score ?? 0
      );

    if (value >= 80) {
      return 'score-good';
    }

    if (value >= 50) {
      return 'score-medium';
    }

    return 'score-low';
  }

  // =========================================================
  // RISK CLASS
  // =========================================================

  getRiskClass(
    risk: string | undefined
  ): string {

    switch (
      String(
        risk ?? ''
      ).toLowerCase()
    ) {

      case 'low':
        return 'risk-low';

      case 'medium':
        return 'risk-medium';

      case 'high':
        return 'risk-high';

      default:
        return '';
    }
  }

  // =========================================================
  // ERROR HANDLING
  // =========================================================

  private handleError(
    error: HttpErrorResponse,
    fallbackMessage: string
  ): void {

    console.error(
      'Compliance API error:',
      error
    );

    if (
      error.status === 422
    ) {

      if (
        Array.isArray(
          error.error?.detail
        )
      ) {

        this.errorMessage =
          error.error.detail
            .map(
              (item: any) =>
                item?.msg ??
                String(item)
            )
            .join(', ');

      } else {

        this.errorMessage =
          error.error?.detail ??
          'Please enter a valid contract ID.';
      }

      return;
    }

    if (
      error.status === 404
    ) {

      this.errorMessage =
        'Contract not found. Please enter an existing contract ID.';

      return;
    }

    if (
      error.status === 401
    ) {

      this.errorMessage =
        'Your session has expired. Please log in again.';

      return;
    }

    this.errorMessage =
      fallbackMessage;
  }
}