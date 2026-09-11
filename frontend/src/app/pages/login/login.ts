import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private http = inject(HttpClient);
  private router = inject(Router);
  private auth = inject(AuthService);

  username = '';
  password = '';

  loading = false;
  error = '';

  login(): void {
    if (!this.username || !this.password) {
      this.error = 'Please enter your username and password.';
      return;
    }

    this.loading = true;
    this.error = '';

    const body = new URLSearchParams();
    body.set('grant_type', 'password');
    body.set('username', this.username);
    body.set('password', this.password);
    body.set('scope', '');
    body.set('client_id', '');
    body.set('client_secret', '');

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    });

    this.http.post<any>(
      'http://127.0.0.1:8000/auth/login',
      body.toString(),
      { headers }
    ).subscribe({
      next: (response) => {
        this.auth.setSession(
          response.access_token,
          response.user_id,
          response.role
        );

        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        console.error('Login error:', err);

        this.loading = false;

        if (err.status === 401) {
          this.error = 'Invalid username or password.';
        } else {
          this.error = 'Unable to connect to the backend.';
        }
      }
    });
  }
}
