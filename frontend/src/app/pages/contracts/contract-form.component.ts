import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ContractsService } from '../../core/data.service';
import { ContractCategory } from '../../core/models';

@Component({
  selector: 'app-contract-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="page-head">
    <div>
      <h1>{{ editingId ? 'Edit contract' : 'New contract' }}</h1>
      <p class="muted">{{ editingId ? 'Update the terms on file.' : 'Add a contract to the repository.' }}</p>
    </div>
    <a routerLink="/contracts" class="btn-ghost">Cancel</a>
  </div>

  <p class="error-banner" *ngIf="error()">{{ error() }}</p>

  <form class="panel form-panel" (ngSubmit)="submit()">
    <div class="field-row">
      <div class="field">
        <label for="title">Title</label>
        <input id="title" [(ngModel)]="title" name="title" required />
      </div>
      <div class="field">
        <label for="num">Contract number</label>
        <input id="num" [(ngModel)]="contractNumber" name="contractNumber" required [disabled]="!!editingId" placeholder="e.g. CIQ-2026-0143" />
      </div>
    </div>

    <div class="field-row">
      <div class="field">
        <label for="cat">Category</label>
        <select id="cat" [(ngModel)]="category" name="category" required>
          <option *ngFor="let c of categories" [value]="c">{{ c }}</option>
        </select>
      </div>
    </div>

    <div class="field">
      <label for="desc">Description</label>
      <textarea id="desc" [(ngModel)]="description" name="description" placeholder="Scope, parties, key terms…"></textarea>
    </div>

    <div class="field-row">
      <div class="field">
        <label for="start">Start date</label>
        <input id="start" type="date" [(ngModel)]="startDate" name="startDate" required />
      </div>
      <div class="field">
        <label for="end">End date</label>
        <input id="end" type="date" [(ngModel)]="endDate" name="endDate" required />
      </div>
    </div>

    <button class="btn" type="submit" [disabled]="saving()">{{ saving() ? 'Saving…' : (editingId ? 'Save changes' : 'Create contract') }}</button>
  </form>
  `,
  styles: [`
    .page-head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; }
    .form-panel { padding: 22px 24px; max-width: 620px; }
  `],
})
export class ContractFormComponent implements OnInit {
  private svc = inject(ContractsService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  editingId: number | null = null;
  title = ''; contractNumber = ''; description = '';
  category: ContractCategory = 'Service Agreement';
  startDate = ''; endDate = '';
  saving = signal(false);
  error = signal('');

  categories: ContractCategory[] = ['Employment Contract', 'Vendor Contract', 'Service Agreement', 'Lease Agreement', 'Purchase Agreement', 'Partnership Agreement', 'Confidentiality Agreement'];

  ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.editingId = Number(idParam);
      this.svc.get(this.editingId).subscribe(c => {
        this.title = c.title;
        this.contractNumber = c.contract_number;
        this.description = c.description || '';
        this.category = c.category;
        this.startDate = c.start_date;
        this.endDate = c.end_date;
      });
    }
  }

  submit() {
    this.error.set('');
    this.saving.set(true);
    const payload: any = { title: this.title, category: this.category, description: this.description, start_date: this.startDate, end_date: this.endDate };
    const req = this.editingId
      ? this.svc.update(this.editingId, payload)
      : this.svc.create({ ...payload, contract_number: this.contractNumber });

    req.subscribe({
      next: (c) => { this.saving.set(false); this.router.navigate(['/contracts', c.id]); },
      error: (e) => {
        this.saving.set(false);
        this.error.set(e.error?.detail ? String(e.error.detail) : 'Unable to save the contract. Check the dates and try again.');
      },
    });
  }
}
