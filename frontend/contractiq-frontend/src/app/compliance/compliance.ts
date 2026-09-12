import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import {
  ComplianceService,
  ComplianceSummary,
  ComplianceRisk
} from '../services/compliance';


@Component({
  selector: 'app-compliance',
  standalone: true,

  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule
  ],

  templateUrl: './compliance.html',
  styleUrl: './compliance.less'
})


export class Compliance implements OnInit {

  summary: ComplianceSummary | null = null;

  riskData: ComplianceRisk[] = [];

  loading = true;

  errorMessage = '';

  isEmpty = false;


  constructor(
    private complianceService: ComplianceService,
    private cdr: ChangeDetectorRef
  ) {}


  // =========================
  // INITIALIZE
  // =========================

  ngOnInit(): void {

    this.loadComplianceData();

  }


  // =========================
  // LOAD COMPLIANCE DATA
  // =========================

  loadComplianceData(): void {

    this.loading = true;

    this.errorMessage = '';

    this.isEmpty = false;


    this.complianceService
      .getComplianceSummary()
      .subscribe({

        next: (data: ComplianceSummary) => {

          console.log(
            'Compliance summary:',
            data
          );


          this.summary = data;

          this.loading = false;


          if (!data || data.total === 0) {

            this.isEmpty = true;

          }


          // Force UI update
          this.cdr.detectChanges();


          // Load risk data
          this.loadRiskData();

        },


        error: (error: any) => {

          console.error(
            'Compliance summary error:',
            error
          );


          this.loading = false;

          this.cdr.detectChanges();


          if (error.status === 401) {

            this.errorMessage =
              'Your session has expired. Please login again.';

          }

          else if (error.status === 403) {

            this.errorMessage =
              'You are not authorized to view compliance data.';

          }

          else if (error.status === 0) {

            this.errorMessage =
              'Unable to connect to the backend server.';

          }

          else {

            this.errorMessage =
              'Failed to load compliance data. Please try again.';

          }


          // Update UI after setting error message
          this.cdr.detectChanges();

        }

      });

  }


  // =========================
  // LOAD RISK DATA
  // =========================

  loadRiskData(): void {

    this.complianceService
      .getRiskReport()
      .subscribe({

        next: (data: ComplianceRisk[]) => {

          console.log(
            'Risk data:',
            data
          );


          this.riskData = data || [];


          // Force UI update
          this.cdr.detectChanges();

        },


        error: (error: any) => {

          console.error(
            'Risk report error:',
            error
          );


          // Risk data failure should not
          // hide the compliance summary.

          this.riskData = [];


          this.cdr.detectChanges();

        }

      });

  }


  // =========================
  // SCORE CLASS
  // =========================

  getScoreClass(score: number): string {

    if (score >= 80) {

      return 'good';

    }


    if (score >= 50) {

      return 'medium';

    }


    return 'poor';

  }


  // =========================
  // RISK CLASS
  // =========================

  getRiskClass(risk: string): string {

    switch (risk) {

      case 'High':

        return 'high';


      case 'Medium':

        return 'medium';


      case 'Low':

        return 'low';


      default:

        return 'default';

    }

  }


  // =========================
  // RETRY
  // =========================

  retry(): void {

    this.loadComplianceData();

  }

}