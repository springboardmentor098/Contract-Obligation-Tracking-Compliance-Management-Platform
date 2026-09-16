import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss'
})
export class Login {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  loading = false;
  error = '';

  loginForm = this.fb.nonNullable.group({
    username: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]]
  });

  submit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.error = '';

    const { username, password } = this.loginForm.getRawValue();

    this.authService.login(username, password).subscribe({
      next: () => {
        this.authService.getCurrentUser().subscribe({
          next: (user) => {
            console.log('Logged-in user:', user);
            console.log('Role:', user.role);

            this.loading = false;
            this.router.navigate(['/dashboard']);
          },

          error: (err) => {
            console.error('Failed to load current user:', err);

            this.authService.logout();
            this.loading = false;
            this.error = 'Unable to load your user profile.';
          }
        });
      },

      error: (err) => {
        console.error('Login error:', err);

        this.loading = false;

        if (err.status === 401) {
          this.error = 'Invalid email or password.';
        } else {
          this.error =
            'Unable to connect to the server. Please try again.';
        }
      }
    });
  }
}
