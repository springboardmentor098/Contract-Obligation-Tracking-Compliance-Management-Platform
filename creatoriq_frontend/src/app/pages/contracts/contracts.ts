import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Contracts as ContractsService, Contract } from '../../services/contracts';

@Component({
  selector: 'app-contracts',
  standalone: true,
  imports: [],
  templateUrl: './contracts.html',
  styleUrl: './contracts.css'
})
export class Contracts implements OnInit {

  contracts: Contract[] = [];

  loading = false;
  errorMessage = '';

  constructor(
    private contractsService: ContractsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadContracts();
  }

  loadContracts(): void {
    this.loading = true;
    this.errorMessage = '';

    this.cdr.detectChanges();

    this.contractsService.getContracts().subscribe({
      next: (data) => {
        console.log('Contracts data received:', data);
        console.log('Contracts count:', data.length);

        this.contracts = data;
        this.loading = false;

        this.cdr.detectChanges();
      },

      error: (error) => {
        console.error('Contracts API error:', error);

        this.loading = false;

        if (error.status === 401) {
          this.errorMessage = 'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.errorMessage = 'You do not have permission to view contracts.';
        } else {
          this.errorMessage = 'Unable to load contracts.';
        }

        this.cdr.detectChanges();
      }
    });
  }
}