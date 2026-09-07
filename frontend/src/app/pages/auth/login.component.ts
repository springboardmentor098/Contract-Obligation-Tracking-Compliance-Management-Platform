import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-head">
        <span class="brand-mark">CIQ</span>
        <h1>ContractIQ</h1>
        <p>Sign in to the obligation &amp; compliance register.</p>
      </div>
      <p class="error-banner" *ngIf="error()">{{ error() }}</p>
      <form (ngSubmit)="submit()">
        <div class="field">
          <label for="email">Email</label>
          <input id="email" type="email" [(ngModel)]="email" name="email" required autocomplete="email" />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input id="password" type="password" [(ngModel)]="password" name="password" required autocomplete="current-password" />
        </div>
        <button class="btn" type="submit" [disabled]="loading()" style="width:100%;justify-content:center;padding:11px">
          {{ loading() ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
      <p class="switch">New to ContractIQ? <a routerLink="/register">Create an account</a></p>
    </div>
  </div>
  `,
  styles: [`
    .auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--ink); padding: 24px; }
    .auth-card { background: var(--surface); border-radius: 4px; padding: 36px 34px; width: 100%; max-width: 380px; }
    .auth-head { text-align: center; margin-bottom: 22px; }
    .brand-mark {
      display: inline-block; font-family: var(--font-mono); font-size: 12px; color: #fff;
      background: var(--ink); border-radius: 3px; padding: 4px 7px; margin-bottom: 12px; letter-spacing: .03em;
    }
    h1 { font-size: 24px; }
    .auth-head p { color: var(--ink-soft); font-size: 13.5px; margin: 4px 0 0; }
    .switch { text-align: center; font-size: 13.5px; color: var(--ink-soft); margin-top: 16px; }
    .switch a { color: var(--seal); font-weight: 500; text-decoration: none; }
  `],
})
export class LoginComponent {
  private auth = inject(AuthService);
  private router = inject(Router);
  email = '';
  password = '';
  loading = signal(false);
  error = signal('');

  submit() {
    this.error.set('');
    this.loading.set(true);
    this.auth.login(this.email, this.password).subscribe({
      next: () => { this.loading.set(false); this.router.navigate(['/dashboard']); },
      error: (e) => {
        this.loading.set(false);
        this.error.set(e.status === 401 ? 'Incorrect email or password.' : 'Unable to sign in. Please try again.');
      },
    });
  }
}
