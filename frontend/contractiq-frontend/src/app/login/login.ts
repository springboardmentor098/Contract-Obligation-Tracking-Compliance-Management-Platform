import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
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
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  templateUrl: './login.html',
  styleUrl: './login.less'
})
export class Login {

  username = '';
  password = '';
  errorMessage = '';

  constructor(
    private auth: Auth,
    private router: Router
  ) {}

  login(): void {

    this.errorMessage = '';

    this.auth.login(this.username, this.password).subscribe({
      next: (response) => {

        console.log('Login successful:', response);

        this.auth.saveToken(response);

        this.router.navigate(['/dashboard']);
      },

      error: (error) => {

        console.error('Login failed:', error);

        this.errorMessage = 'Invalid email or password.';
      }
    });
  }
}