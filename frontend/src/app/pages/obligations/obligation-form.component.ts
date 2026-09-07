import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ObligationsService, ContractsService } from '../../core/data.service';
import { ObligationType, ContractListItem } from '../../core/models';

@Component({
  selector: 'app-obligation-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="page-head">
    <div>
      <h1>Register obligation</h1>
      <p class="muted">Attach a payment, delivery, or compliance obligation to a contract.</p>
    </div>
    <a routerLink="/obligations" class="btn-ghost">Cancel</a>
  </div>

  <p class="error-banner" *ngIf="error()">{{ error() }}</p>

  <form class="panel form-panel" (ngSubmit)="submit()">
    <div class="field">
      <label for="contract">Contract</label>
      <select id="contract" [(ngModel)]="contractId" name="contractId" required>
        <option [ngValue]="null" disabled>Select a contract…</option>
        <option *ngFor="let c of contracts()" [ngValue]="c.id">{{ c.contract_number }} — {{ c.title }}</option>
      </select>
    </div>

    <div class="field">
      <label for="title">Title</label>
      <input id="title" [(ngModel)]="title" name="title" required />
    </div>

    <div class="field-row">
      <div class="field">
        <label for="type">Obligation type</label>
        <select id="type" [(ngModel)]="obligationType" name="obligationType" required>
          <option *ngFor="let t of types" [value]="t">{{ t }}</option>
        </select>
      </div>
      <div class="field">
        <label for="due">Due date</label>
        <input id="due" type="date" [(ngModel)]="dueDate" name="dueDate" required />
      </div>
    </div>

    <div class="field">
      <label for="desc">Description</label>
      <textarea id="desc" [(ngModel)]="description" name="description" placeholder="What must be delivered, and by whom…"></textarea>
    </div>

    <button class="btn" type="submit" [disabled]="saving()">{{ saving() ? 'Saving…' : 'Register obligation' }}</button>
  </form>
  `,
  styles: [`
    .page-head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; }
    .form-panel { padding: 22px 24px; max-width: 620px; }
  `],
})
export class ObligationFormComponent implements OnInit {
  private svc = inject(ObligationsService);
  private contractsSvc = inject(ContractsService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  contracts = signal<ContractListItem[]>([]);
  contractId: number | null = null;
  title = ''; description = ''; dueDate = '';
  obligationType: ObligationType = 'Payment Obligation';
  saving = signal(false);
  error = signal('');

  types: ObligationType[] = ['Payment Obligation', 'Delivery Commitment', 'Reporting Requirement', 'Renewal Condition', 'Service Level Agreement', 'Legal Compliance Requirement'];

  ngOnInit() {
    this.contractsSvc.list().subscribe(list => this.contracts.set(list));
    const qp = this.route.snapshot.queryParamMap.get('contractId');
    if (qp) this.contractId = Number(qp);
  }

  submit() {
    this.error.set('');
    this.saving.set(true);
    this.svc.create({
      contract_id: this.contractId,
      title: this.title,
      description: this.description,
      obligation_type: this.obligationType,
      due_date: this.dueDate,
    }).subscribe({
      next: (o) => { this.saving.set(false); this.router.navigate(['/contracts', o.contract_id]); },
      error: (e) => {
        this.saving.set(false);
        this.error.set(e.error?.detail ? String(e.error.detail) : 'Unable to register the obligation.');
      },
    });
  }
}
