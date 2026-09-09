import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { LoginResponse } from '../models';
import { environment } from '../../environments/environment';

const TOKEN_KEY = 'contractiq_access_token';
const USER_KEY = 'contractiq_user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly isAuthenticated = signal(Boolean(localStorage.getItem(TOKEN_KEY)));
  readonly currentUser = signal<{ user_id: number; role: string } | null>(this.readUser());
  constructor(private http: HttpClient, private router: Router) {}
  login(email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.apiBaseUrl}/auth/login`, { email, password }).pipe(tap((response) => {
      localStorage.setItem(TOKEN_KEY, response.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify({ user_id: response.user_id, role: response.role }));
      this.isAuthenticated.set(true); this.currentUser.set({ user_id: response.user_id, role: response.role });
    }));
  }
  logout(): void { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); this.isAuthenticated.set(false); this.currentUser.set(null); void this.router.navigate(['/login']); }
  private readUser(): { user_id: number; role: string } | null { const stored = localStorage.getItem(USER_KEY); return stored ? JSON.parse(stored) : null; }
}