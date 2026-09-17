import {
  Component,
  ChangeDetectorRef,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import { Router } from '@angular/router';

import { finalize } from 'rxjs';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';

import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,

  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],

  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {

  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);

  isLoading = false;
  errorMessage = '';

  loginForm = this.fb.group({

    username: [
      '',
      [
        Validators.required
      ]
    ],

    password: [
      '',
      [
        Validators.required
      ]
    ]

  });

  onLogin(): void {

    this.errorMessage = '';

    if (this.loginForm.invalid) {

      this.loginForm.markAllAsTouched();

      return;
    }

    if (this.isLoading) {
      return;
    }

    const username =
      (this.loginForm.value.username || '').trim();

    const password =
      this.loginForm.value.password || '';

    if (!username || !password) {

      this.errorMessage =
        'Please enter username and password.';

      return;
    }

    console.log('Starting login for:', username);

    this.isLoading = true;

    this.cdr.detectChanges();

    this.authService
      .login(username, password)

      .pipe(

        finalize(() => {

          this.isLoading = false;

          this.cdr.detectChanges();

          console.log(
            'Login request completed.'
          );
        })

      )

      .subscribe({

        next: (response) => {

          console.log(
            'Login successful.',
            response
          );

          const token =
            this.authService.getToken();

          console.log(
            'Token available after login:',
            !!token
          );

          if (!token) {

            this.errorMessage =
              'Login succeeded, but the authentication token was not saved.';

            this.cdr.detectChanges();

            return;
          }

          console.log(
            'Navigating to dashboard...'
          );

          this.router
            .navigateByUrl('/dashboard')
            .then((success) => {

              console.log(
                'Dashboard navigation result:',
                success
              );

              if (!success) {

                this.errorMessage =
                  'Login succeeded, but dashboard navigation failed.';

                this.cdr.detectChanges();
              }

            })

            .catch((error) => {

              console.error(
                'Dashboard navigation error:',
                error
              );

              this.errorMessage =
                'Login succeeded, but the dashboard could not be opened.';

              this.cdr.detectChanges();
            });
        },

        error: (error) => {

          console.error(
            'Login failed:',
            error
          );

          this.authService.logout();

          if (error?.status === 401) {

            this.errorMessage =
              'Invalid username or password.';

          } else if (error?.status === 400) {

            this.errorMessage =
              'Invalid login details.';

          } else if (error?.status === 422) {

            this.errorMessage =
              'Please enter a valid username and password.';

          } else if (error?.status === 0) {

            this.errorMessage =
              'Unable to connect to the server. Please make sure FastAPI is running.';

          } else if (error?.status === 500) {

            this.errorMessage =
              'Server error occurred. Please check the backend.';

          } else {

            this.errorMessage =
              'Unable to login. Please try again.';
          }

          this.cdr.detectChanges();
        }

      });
  }
}