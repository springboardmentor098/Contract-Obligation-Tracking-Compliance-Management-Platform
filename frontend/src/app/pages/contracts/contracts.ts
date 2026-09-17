import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface Contract {
  id: number;
  title: string;
  contract_number: string;
  category: string;
  description: string | null;
  start_date: string;
  end_date: string;
  status: string;
  created_by: number;
  assigned_to: number | null;
  reviewed_at: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-contracts',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './contracts.html',
  styleUrl: './contracts.scss',
})
export class Contracts implements OnInit {
  constructor() {
    console.log('CONTRACTS COMPONENT LOADED');
  }
  private http = inject(HttpClient);

  contracts = signal<Contract[]>([]);

  loading = signal(false);
  error = '';

  showCreateForm = false;
  saving = false;

  newContract = {
    title: '',
    contract_number: '',
    category: '',
    description: '',
    start_date: '',
    end_date: '',
  };

  ngOnInit(): void {
    console.log('CONTRACTS NGONINIT');
    this.loadContracts();
  }

  private headers(): HttpHeaders {
    const token = localStorage.getItem('access_token');

    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    });
  }

  loadContracts(): void {
    console.log('CONTRACTS: loadContracts() START');

    this.loading.set(true);
    this.error = '';

    const token = localStorage.getItem('access_token');

    console.log('CONTRACTS: token exists =', !!token);

    this.http.get<Contract[]>(
      'http://127.0.0.1:8000/contracts',
      {
        headers: this.headers()
      }
    ).subscribe({
      next: (data) => {
        console.log('CONTRACTS: API SUCCESS');
        console.log('CONTRACTS: received data =', data);
        console.log('CONTRACTS: received count =', data.length);

        this.contracts.set(data);
        this.loading.set(false);

        console.log('CONTRACTS: loading =', this.loading());
      },
      error: (err) => {
        console.error('CONTRACTS: API ERROR', err);

        this.loading.set(false);

        this.error =
          err.error?.detail ||
          'Unable to load contracts.';

        console.log('CONTRACTS: loading =', this.loading());
      },
      complete: () => {
        console.log('CONTRACTS: HTTP REQUEST COMPLETE');
      }
    });
  }

  openCreateForm(): void {
    this.showCreateForm = true;
    this.error = '';
  }

  closeCreateForm(): void {
    this.showCreateForm = false;
  }

  createContract(): void {
    if (
      !this.newContract.title ||
      !this.newContract.contract_number ||
      !this.newContract.category ||
      !this.newContract.start_date ||
      !this.newContract.end_date
    ) {
      this.error = 'Please fill in all required fields.';
      return;
    }

    this.saving = true;
    this.error = '';

    this.http.post<Contract>(
      'http://127.0.0.1:8000/contracts',
      this.newContract,
      { headers: this.headers() }
    ).subscribe({
      next: () => {
        this.saving = false;
        this.showCreateForm = false;

        this.newContract = {
          title: '',
          contract_number: '',
          category: '',
          description: '',
          start_date: '',
          end_date: '',
        };

        this.loadContracts();
      },
      error: (err) => {
        console.error('Failed to create contract:', err);
        this.saving = false;

        this.error =
          err.error?.detail ||
          'Unable to create contract.';
      }
    });
  }

  submitForReview(contract: Contract): void {
    this.http.post<Contract>(
      `http://127.0.0.1:8000/contracts/${contract.id}/submit-review`,
      {},
      { headers: this.headers() }
    ).subscribe({
      next: (updated) => {
        contract.status = updated.status;
        contract.reviewed_at = updated.reviewed_at;
        contract.updated_at = updated.updated_at;
      },
      error: (err) => {
        console.error('Failed to submit contract:', err);
        this.error =
          err.error?.detail ||
          'Unable to submit contract for review.';
      }
    });
  }

  approveContract(contract: Contract): void {
    this.http.post<Contract>(
      `http://127.0.0.1:8000/contracts/${contract.id}/approve`,
      {},
      { headers: this.headers() }
    ).subscribe({
      next: (updated) => {
        contract.status = updated.status;
        contract.approved_at = updated.approved_at;
        contract.updated_at = updated.updated_at;
      },
      error: (err) => {
        console.error('Failed to approve contract:', err);
        this.error =
          err.error?.detail ||
          'Unable to approve contract.';
      }
    });
  }

  activateContract(contract: Contract): void {
    this.http.post<Contract>(
      `http://127.0.0.1:8000/contracts/${contract.id}/activate`,
      {},
      { headers: this.headers() }
    ).subscribe({
      next: (updated) => {
        contract.status = updated.status;
        contract.updated_at = updated.updated_at;
      },
      error: (err) => {
        console.error('Failed to activate contract:', err);
        this.error =
          err.error?.detail ||
          'Unable to activate contract.';
      }
    });
  }

  getStatusClass(status: string): string {
    return status.toLowerCase().replace(/\s+/g, '-');
  }
}
