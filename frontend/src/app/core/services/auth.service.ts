import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface LoginResponse {
  access_token: string;
  token_type?: string;
}

export interface AuthUser {
  id: number;
  email: string;
  username?: string;
  full_name?: string;
  role?: string;
  is_active?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl = environment.apiUrl;
  private readonly tokenKey = 'contractiq_access_token';
  private readonly userKey = 'contractiq_user';

  login(username: string, password: string): Observable<LoginResponse> {
    const body = new HttpParams()
      .set('username', username)
      .set('password', password);

    return this.http
      .post<LoginResponse>(`${this.apiUrl}/auth/login`, body.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      .pipe(
        tap((response) => {
          localStorage.setItem(this.tokenKey, response.access_token);
        })
      );
  }

  getCurrentUser(): Observable<AuthUser> {
    return this.http.get<AuthUser>(`${this.apiUrl}/auth/me`).pipe(
      tap((user) => {
        localStorage.setItem(this.userKey, JSON.stringify(user));
      })
    );
  }

  getStoredUser(): AuthUser | null {
    const user = localStorage.getItem(this.userKey);

    if (!user) {
      return null;
    }

    try {
      return JSON.parse(user) as AuthUser;
    } catch {
      return null;
    }
  }

  getRole(): string | null {
    return this.getStoredUser()?.role ?? null;
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }
}
