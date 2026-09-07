import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UsersService } from '../../core/data.service';
import { User, UserRole } from '../../core/models';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
  <div class="page-head">
    <h1>Users</h1>
    <p class="muted">Manage roles and access across the platform.</p>
  </div>

  <p class="error-banner" *ngIf="error()">{{ error() }}</p>

  <div class="panel" *ngIf="users().length; else empty">
    <table class="ledger">
      <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th></th></tr></thead>
      <tbody>
        <tr *ngFor="let u of users()">
          <td>{{ u.full_name }}</td>
          <td>{{ u.email }}</td>
          <td>
            <select [ngModel]="u.role" (ngModelChange)="changeRole(u, $event)">
              <option *ngFor="let r of roles" [value]="r">{{ r }}</option>
            </select>
          </td>
          <td><span class="tag" [ngClass]="u.is_active ? 'tag-seal' : 'tag-rose'">{{ u.is_active ? 'Active' : 'Inactive' }}</span></td>
          <td><button class="btn-ghost btn-sm" *ngIf="u.is_active" (click)="deactivate(u)">Deactivate</button></td>
        </tr>
      </tbody>
    </table>
  </div>
  <ng-template #empty><div class="panel empty-state"><strong>No users found</strong></div></ng-template>
  `,
  styles: [`
    .page-head { margin-bottom: 18px; }
    select { border: 1px solid var(--line-strong); border-radius: var(--radius); padding: 6px 9px; background: var(--surface); }
  `],
})
export class UsersComponent implements OnInit {
  private svc = inject(UsersService);
  users = signal<User[]>([]);
  error = signal('');
  roles: UserRole[] = ['Employee', 'Department Head', 'Contract Manager', 'Compliance Officer', 'Legal Manager', 'Administrator'];

  ngOnInit() {
    this.svc.list().subscribe({
      next: list => this.users.set(list),
      error: () => this.error.set('Unable to load users.'),
    });
  }

  changeRole(u: User, role: UserRole) {
    this.svc.updateRole(u.id, role).subscribe({
      next: updated => this.users.set(this.users().map(x => x.id === updated.id ? updated : x)),
      error: () => this.error.set('Unable to update that role.'),
    });
  }

  deactivate(u: User) {
    this.svc.deactivate(u.id).subscribe({
      next: () => this.users.set(this.users().map(x => x.id === u.id ? { ...x, is_active: false } : x)),
      error: () => this.error.set('Unable to deactivate that user.'),
    });
  }
}
