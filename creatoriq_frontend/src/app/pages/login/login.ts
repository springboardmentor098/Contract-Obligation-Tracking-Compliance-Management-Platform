import { ChangeDetectorRef, Component } from '@angular/core';
import {
  ReactiveFormsModule,
  FormBuilder,
  Validators
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  loading = false;
  errorMessage = '';
  loginForm;

  constructor(
    private fb: FormBuilder,
    private auth: Auth,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.loginForm = this.fb.nonNullable.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  login(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      this.cdr.detectChanges();
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.cdr.detectChanges();

    this.auth.login(this.loginForm.getRawValue()).subscribe({
      next: () => {
        this.loading = false;
        this.cdr.detectChanges();
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        console.error('Login error:', error);

        this.loading = false;

        if (error.status === 401) {
          this.errorMessage = 'Invalid email or password.';
        } else if (error.status === 403) {
          this.errorMessage =
            'You do not have permission to access the application.';
        } else {
          this.errorMessage = 'Unable to connect to the server.';
        }

        this.cdr.detectChanges();
      }
    });
  }
}