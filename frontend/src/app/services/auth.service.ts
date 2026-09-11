import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly baseUrl = 'http://127.0.0.1:8000';
  private readonly tokenKey = 'access_token';
  private readonly userIdKey = 'user_id';
  private readonly roleKey = 'role';

  private http = inject(HttpClient);

  login(username: string, password: string): Observable<LoginResponse> {
    const body = new URLSearchParams();

    body.set('grant_type', 'password');
    body.set('username', username);
    body.set('password', password);
    body.set('scope', '');
    body.set('client_id', '');
    body.set('client_secret', '');

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    });

    return this.http.post<LoginResponse>(
      `${this.baseUrl}/auth/login`,
      body.toString(),
      { headers }
    );
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getUserId(): string | null {
    return localStorage.getItem(this.userIdKey);
  }

  getRole(): string | null {
    return localStorage.getItem(this.roleKey);
  }

  setSession(
    accessToken: string,
    userId?: number | string,
    role?: string
  ): void {
    localStorage.setItem(this.tokenKey, accessToken);

    if (userId !== undefined && userId !== null) {
      localStorage.setItem(this.userIdKey, String(userId));
    }

    if (role) {
      localStorage.setItem(this.roleKey, role);
    }
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userIdKey);
    localStorage.removeItem(this.roleKey);
  }
}
