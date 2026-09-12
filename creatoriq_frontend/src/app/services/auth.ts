import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CurrentUser {
  id: number;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
}

interface JwtPayload {
  sub?: string;
  role?: string;
  exp?: number;
  [key: string]: unknown;
}

@Injectable({
  providedIn: 'root'
})
export class Auth {

  private readonly apiUrl = 'http://127.0.0.1:8000/users';

  constructor(private http: HttpClient) {}

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `${this.apiUrl}/login`,
      credentials
    ).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
      })
    );
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  logout(): void {
    localStorage.removeItem('access_token');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getRole(): string | null {
    const token = this.getToken();

    if (!token) {
      return null;
    }

    const payload = this.decodeToken(token);

    return payload?.role ?? null;
  }

  getUserId(): number | null {
    const token = this.getToken();

    if (!token) {
      return null;
    }

    const payload = this.decodeToken(token);

    if (!payload?.sub) {
      return null;
    }

    const userId = Number(payload.sub);

    return Number.isNaN(userId) ? null : userId;
  }

  getCurrentUser(): Observable<CurrentUser> {
    const userId = this.getUserId();

    return this.http.get<CurrentUser>(
      `${this.apiUrl}/${userId}`
    );
  }

  hasRole(role: string): boolean {
    return this.getRole() === role;
  }

  private decodeToken(token: string): JwtPayload | null {
    try {
      const payload = token.split('.')[1];

      if (!payload) {
        return null;
      }

      const decodedPayload = atob(
        payload.replace(/-/g, '+').replace(/_/g, '/')
      );

      return JSON.parse(decodedPayload) as JwtPayload;
    } catch (error) {
      console.error(
        'Unable to decode authentication token:',
        error
      );

      return null;
    }
  }
}