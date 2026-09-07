import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { User, UserRole } from './models';
import { API_BASE } from './api-base';

interface TokenResponse { access_token: string; token_type: string; }

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  private _user = signal<User | null>(this.readCachedUser());
  user = this._user.asReadonly();
  isAuthenticated = computed(() => !!this.token);

  get token(): string | null {
    return localStorage.getItem('contractiq_token');
  }

  private readCachedUser(): User | null {
    const raw = localStorage.getItem('contractiq_user');
    return raw ? JSON.parse(raw) : null;
  }

  login(email: string, password: string): Observable<TokenResponse> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);
    return this.http.post<TokenResponse>(`${API_BASE}/auth/login`, body.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).pipe(tap(res => {
      localStorage.setItem('contractiq_token', res.access_token);
      this.fetchMe().subscribe();
    }));
  }

  register(payload: { full_name: string; email: string; password: string; role: UserRole }): Observable<User> {
    return this.http.post<User>(`${API_BASE}/auth/register`, payload);
  }

  fetchMe(): Observable<User> {
    return this.http.get<User>(`${API_BASE}/users/me`).pipe(tap(u => {
      this._user.set(u);
      localStorage.setItem('contractiq_user', JSON.stringify(u));
    }));
  }

  logout(): void {
    localStorage.removeItem('contractiq_token');
    localStorage.removeItem('contractiq_user');
    this._user.set(null);
    this.router.navigate(['/login']);
  }

  hasRole(...roles: UserRole[]): boolean {
    const u = this._user();
    return !!u && roles.includes(u.role);
  }
}
