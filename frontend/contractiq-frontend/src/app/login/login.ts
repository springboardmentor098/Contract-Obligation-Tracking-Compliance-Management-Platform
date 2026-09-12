import { Component } from '@angular/core';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators
} from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';

import { Router } from '@angular/router';

import { Auth } from '../services/auth';


@Component({
  selector: 'app-login',
  standalone: true,

  imports: [
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],

  templateUrl: './login.html',
  styleUrl: './login.less'
})
export class Login {

  loginForm: FormGroup;

  errorMessage = '';

  loading = false;


  constructor(
    private fb: FormBuilder,
    private auth: Auth,
    private router: Router
  ) {

    this.loginForm = this.fb.group({

      username: [
        '',
        [
          Validators.required,
          Validators.email
        ]
      ],

      password: [
        '',
        [
          Validators.required,
          Validators.minLength(6)
        ]
      ]

    });

  }


  // ===============================
  // Login
  // ===============================

  login(): void {

    this.errorMessage = '';

    // Check form validation
    if (this.loginForm.invalid) {

      this.loginForm.markAllAsTouched();

      return;
    }


    this.loading = true;


    const username =
      this.loginForm.get('username')?.value;

    const password =
      this.loginForm.get('password')?.value;


    this.auth
      .login(username, password)
      .subscribe({

        next: (response) => {

          console.log(
            'Login successful:',
            response
          );

          this.auth.saveToken(response);

          this.loading = false;


          this.router.navigate([
            '/dashboard'
          ]);

        },


        error: (error) => {

          console.error(
            'Login failed:',
            error
          );

          this.loading = false;

          this.errorMessage =
            'Invalid email or password. Please try again.';

        }

      });

  }


  // ===============================
  // Forgot Password
  // ===============================

  forgotPassword(): void {

    this.errorMessage =
      'Password reset feature is coming soon.';

  }

}