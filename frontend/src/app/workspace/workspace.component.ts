import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin, finalize } from 'rxjs';
import { ApiService } from '../services/api.service';

interface Row { [key: string]: any }

@Component({
  selector: 'app-workspace',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './workspace.component.html',
  styleUrl: './workspace.component.scss',
})
export class WorkspaceComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);
  private readonly changeDetector = inject(ChangeDetectorRef);
  section = this.route.snapshot.data['section'] as string;
  rows: Row[] = [];
  summary: any = null;
  loading = true;
  saving = false;
  error = '';
  notice = '';
  search = '';
  showForm = false;
  editingId: number | null = null;
  form = this.fb.nonNullable.group({
    title: ['', Validators.required], contract_number: ['', Validators.required], category: ['Service Agreement', Validators.required],
    start_date: [''], end_date: [''], contract_id: ['', Validators.required], obligation_type: ['Reporting Requirement', Validators.required],
    due_date: ['', Validators.required], assigned_to: ['', Validators.required], renewal_date: ['', Validators.required],
    previous_expiry_date: ['', Validators.required], new_expiry_date: [''], notification_type: ['Contract Status Alert', Validators.required],
    message: ['', Validators.required],
  });

  constructor() { this.load(); }

  get title(): string { return this.section === 'audit' ? 'Audit history' : this.section[0].toUpperCase() + this.section.slice(1); }
  get filteredRows(): Row[] {
    const query = this.search.trim().toLowerCase();
    return query ? this.rows.filter(row => Object.values(row).some(value => String(value ?? '').toLowerCase().includes(query))) : this.rows;
  }
  get isCrud(): boolean { return ['contracts', 'obligations', 'renewals', 'notifications'].includes(this.section); }
  get columns(): string[] {
    if (this.section === 'contracts') return ['contract_number', 'title', 'category', 'status', 'start_date', 'end_date'];
    if (this.section === 'obligations') return ['title', 'obligation_type', 'due_date', 'status', 'assigned_to'];
    if (this.section === 'renewals') return ['contract_id', 'renewal_date', 'previous_expiry_date', 'status', 'new_expiry_date'];
    if (this.section === 'notifications') return ['notification_type', 'title', 'message', 'status', 'created_at'];
    return [];
  }

  load(): void {
    this.loading = true; this.error = ''; this.summary = null;
    if (this.section === 'audit') {
      this.rows = [];
      this.loading = false;
      return;
    }
    let request = this.api.list<Row[]>(this.pathForSection());
    if (this.section === 'reports') {
      request = forkJoin({ contracts: this.api.list<Row>('/reports/contracts/summary'), obligations: this.api.list<Row>('/reports/obligations/summary'), renewals: this.api.list<Row>('/reports/renewals/summary'), compliance: this.api.list<Row>('/reports/compliance/summary') }) as any;
    }
    if (this.section === 'compliance') request = this.api.list<Row[]>('/compliance/');
    request.pipe(finalize(() => { this.loading = false; this.changeDetector.markForCheck(); })).subscribe({ next: (data: any) => { this.summary = this.section === 'reports' ? data : null; this.rows = Array.isArray(data) ? data : []; this.changeDetector.markForCheck(); }, error: (error) => { this.error = error.status === 401 ? 'Your session has expired. Please sign in again.' : 'This workspace could not load from the API.'; this.changeDetector.markForCheck(); } });
  }

  private pathForSection(): string {
    if (this.section === 'audit') return '/audit';
    return `/${this.section}`;
  }

  submit(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.saving = true; this.error = ''; const wasEditing = this.editingId !== null; const value = this.form.getRawValue();
    let request;
    if (this.section === 'contracts') {
      const body = { title: value.title, contract_number: value.contract_number, category: value.category, start_date: value.start_date || null, end_date: value.end_date || null };
      request = this.editingId ? this.api.update(`/contracts/${this.editingId}`, body) : this.api.create('/contracts', body);
    } else if (this.section === 'obligations') {
      const body = { contract_id: Number(value.contract_id), title: value.title, obligation_type: value.obligation_type, due_date: value.due_date, assigned_to: Number(value.assigned_to) };
      request = this.editingId ? this.api.update(`/obligations/${this.editingId}`, body) : this.api.create('/obligations', body);
    } else if (this.section === 'renewals') {
      const body = { contract_id: Number(value.contract_id), renewal_date: value.renewal_date, previous_expiry_date: value.previous_expiry_date, new_expiry_date: value.new_expiry_date || null, assigned_to: value.assigned_to ? Number(value.assigned_to) : null };
      request = this.editingId ? this.api.update(`/renewals/${this.editingId}`, body) : this.api.create('/renewals', body);
    }
    else request = this.api.create('/notifications', { user_id: Number(value.assigned_to), notification_type: value.notification_type, title: value.title, message: value.message });
    request.pipe(finalize(() => this.saving = false)).subscribe({ next: () => { this.showForm = false; this.editingId = null; this.notice = `${this.title.slice(0, -1)} ${wasEditing ? 'updated' : 'created'} successfully.`; this.form.reset({ category: 'Service Agreement', obligation_type: 'Reporting Requirement', notification_type: 'Contract Status Alert' }); this.load(); }, error: () => this.error = 'The record could not be saved. Check the values and your permissions.' });
  }

  edit(row: Row): void {
    this.editingId = row['id'];
    this.showForm = true;
    this.form.patchValue({
      title: row['title'] ?? '', contract_number: row['contract_number'] ?? '', category: row['category'] ?? 'Service Agreement',
      start_date: row['start_date'] ?? '', end_date: row['end_date'] ?? '', contract_id: String(row['contract_id'] ?? ''),
      obligation_type: row['obligation_type'] ?? 'Reporting Requirement', due_date: row['due_date'] ?? '', assigned_to: String(row['assigned_to'] ?? ''),
      renewal_date: row['renewal_date'] ?? '', previous_expiry_date: row['previous_expiry_date'] ?? '', new_expiry_date: row['new_expiry_date'] ?? '',
    });
  }

  changeStatus(row: Row, status: string): void {
    const path = this.section === 'contracts' ? `/contracts/${row['id']}/status` : this.section === 'obligations' ? `/obligations/${row['id']}/status` : `/renewals/${row['id']}/status`;
    this.api.patch(path, { status }).subscribe({ next: () => { this.notice = 'Status updated.'; this.load(); }, error: () => this.error = 'This status transition is not allowed by the backend workflow.' });
  }

  markRead(row: Row): void { this.api.patch(`/notifications/${row['id']}/read`).subscribe({ next: () => this.load(), error: () => this.error = 'Notification could not be marked as read.' }); }
  deleteContract(row: Row): void { if (!confirm(`Delete ${row['contract_number']}?`)) return; this.api.remove(`/contracts/${row['id']}`).subscribe({ next: () => this.load(), error: () => this.error = 'Contract could not be deleted.' }); }
  exportReport(type: string, extension: string): void {
    this.api.download(`/reports/${type}/export/${extension}`).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${type}-report.${extension === 'excel' ? 'xlsx' : 'pdf'}`;
        link.click();
        URL.revokeObjectURL(url);
      },
      error: () => this.error = 'The report could not be downloaded. Check your permissions and try again.',
    });
  }
}
