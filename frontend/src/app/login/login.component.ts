import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Component({ selector: 'app-login', standalone: true, imports: [CommonModule, ReactiveFormsModule], templateUrl: './login.component.html', styleUrl: './login.component.scss' })
export class LoginComponent {
  private readonly formBuilder = inject(FormBuilder); private readonly auth = inject(AuthService); private readonly router = inject(Router);
  readonly form = this.formBuilder.nonNullable.group({ email: ['', [Validators.required, Validators.email]], password: ['', [Validators.required, Validators.minLength(6)]] });
  loading = false; error = '';
  submit(): void { if (this.form.invalid) { this.form.markAllAsTouched(); return; } this.loading = true; this.error = ''; const { email, password } = this.form.getRawValue(); this.auth.login(email, password).pipe(finalize(() => (this.loading = false))).subscribe({ next: () => void this.router.navigate(['/dashboard']), error: (error) => (this.error = error.status === 401 ? 'The email or password is incorrect.' : 'Unable to connect to ContractIQ.') }); }
}