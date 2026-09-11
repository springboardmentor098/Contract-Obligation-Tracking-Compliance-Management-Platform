import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthResponse, User } from '../models/models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  private readonly baseUrl = environment.apiUrl;

  login(email: string, password: string): Observable<AuthResponse> {

    const body = new URLSearchParams();

    // FastAPI OAuth2PasswordRequestForm expects "username"
    body.set('username', email);
    body.set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http.post<AuthResponse>(
      `${this.baseUrl}/auth/login`,
      body.toString(),
      { headers }
    ).pipe(
      tap(response => {

        // Store JWT token
        localStorage.setItem(
          'contractiq_token',
          response.access_token
        );

        // Backend currently doesn't return user information,
        // so don't depend on response.user.
        if (response.user) {
          localStorage.setItem(
            'contractiq_user',
            JSON.stringify(response.user)
          );
        }
      })
    );
  }

  logout(): void {
    localStorage.removeItem('contractiq_token');
    localStorage.removeItem('contractiq_user');

    this.router.navigate(['/login']);
  }

  token(): string | null {
    return localStorage.getItem('contractiq_token');
  }

  isAuthenticated(): boolean {
    return !!this.token();
  }

  currentUser(): User | null {

    const raw = localStorage.getItem('contractiq_user');

    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw) as User;
    } catch {
      return null;
    }
  }
}