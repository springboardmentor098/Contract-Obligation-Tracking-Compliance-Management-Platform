import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth.service';
import { UserRole } from '../../core/models';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-head">
        <span class="brand-mark">CIQ</span>
        <h1>Create an account</h1>
        <p>Register to start tracking contracts and obligations.</p>
      </div>
      <p class="error-banner" *ngIf="error()">{{ error() }}</p>
      <p class="error-banner" style="background:var(--seal-soft);color:var(--seal);border-color:#bcd6cc" *ngIf="success()">
        Account created. You can sign in now.
      </p>
      <form (ngSubmit)="submit()" *ngIf="!success()">
        <div class="field">
          <label for="name">Full name</label>
          <input id="name" [(ngModel)]="fullName" name="fullName" required />
        </div>
        <div class="field">
          <label for="email">Email</label>
          <input id="email" type="email" [(ngModel)]="email" name="email" required />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input id="password" type="password" [(ngModel)]="password" name="password" required minlength="6" />
        </div>
        <div class="field">
          <label for="role">Role</label>
          <select id="role" [(ngModel)]="role" name="role">
            <option *ngFor="let r of roles" [value]="r">{{ r }}</option>
          </select>
        </div>
        <button class="btn" type="submit" [disabled]="loading()" style="width:100%;justify-content:center;padding:11px">
          {{ loading() ? 'Creating…' : 'Create account' }}
        </button>
      </form>
      <p class="switch">Already registered? <a routerLink="/login">Sign in</a></p>
    </div>
  </div>
  `,
  styles: [`
    .auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--ink); padding: 24px; }
    .auth-card { background: var(--surface); border-radius: 4px; padding: 36px 34px; width: 100%; max-width: 400px; }
    .auth-head { text-align: center; margin-bottom: 22px; }
    .brand-mark {
      display: inline-block; font-family: var(--font-mono); font-size: 12px; color: #fff;
      background: var(--ink); border-radius: 3px; padding: 4px 7px; margin-bottom: 12px; letter-spacing: .03em;
    }
    h1 { font-size: 22px; }
    .auth-head p { color: var(--ink-soft); font-size: 13.5px; margin: 4px 0 0; }
    .switch { text-align: center; font-size: 13.5px; color: var(--ink-soft); margin-top: 16px; }
    .switch a { color: var(--seal); font-weight: 500; text-decoration: none; }
  `],
})
export class RegisterComponent {
  private auth = inject(AuthService);
  fullName = ''; email = ''; password = '';
  role: UserRole = 'Employee';
  roles: UserRole[] = ['Employee', 'Department Head', 'Contract Manager', 'Compliance Officer', 'Legal Manager', 'Administrator'];
  loading = signal(false);
  error = signal('');
  success = signal(false);

  submit() {
    this.error.set('');
    this.loading.set(true);
    this.auth.register({ full_name: this.fullName, email: this.email, password: this.password, role: this.role }).subscribe({
      next: () => { this.loading.set(false); this.success.set(true); },
      error: (e) => {
        this.loading.set(false);
        this.error.set(e.status === 400 ? 'That email is already registered.' : 'Unable to create the account.');
      },
    });
  }
}
