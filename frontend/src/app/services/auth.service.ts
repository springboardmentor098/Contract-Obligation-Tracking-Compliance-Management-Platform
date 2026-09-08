import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: string;
}

export enum UserRole {
  ADMINISTRATOR = 'Administrator',
  LEGAL_MANAGER = 'Legal Manager',
  COMPLIANCE_OFFICER = 'Compliance Officer',
  CONTRACT_MANAGER = 'Contract Manager',
  DEPARTMENT_HEAD = 'Department Head',
  EMPLOYEE = 'Employee'
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://127.0.0.1:8000/auth';

  private readonly tokenKey = 'access_token';
  private readonly roleKey = 'user_role';

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(
        `${this.apiUrl}/login`,
        credentials
      )
      .pipe(
        tap((response) => {
          localStorage.setItem(
            this.tokenKey,
            response.access_token
          );

          localStorage.setItem(
            this.roleKey,
            response.role
          );
        })
      );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.roleKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  getRole(): string | null {
    return localStorage.getItem(this.roleKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  hasRole(role: UserRole): boolean {
    return this.getRole() === role;
  }

  hasAnyRole(roles: UserRole[]): boolean {
    const currentRole = this.getRole();

    return currentRole !== null &&
      roles.includes(currentRole as UserRole);
  }
}