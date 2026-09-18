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


  // ============================================================
  // LOGIN
  // ============================================================

  login(
    email: string,
    password: string
  ): Observable<AuthResponse> {

    const body = new URLSearchParams();

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


        // If backend already returns user information,
        // store it immediately.
        if (response.user) {

          localStorage.setItem(
            'contractiq_user',
            JSON.stringify(response.user)
          );

        }

      })

    );

  }


  // ============================================================
  // LOGOUT
  // ============================================================

  logout(): void {

    localStorage.removeItem('contractiq_token');

    localStorage.removeItem('contractiq_user');

    this.router.navigate(['/login']);

  }


  // ============================================================
  // GET JWT TOKEN
  // ============================================================

  token(): string | null {

    return localStorage.getItem(
      'contractiq_token'
    );

  }


  // ============================================================
  // AUTHENTICATION CHECK
  // ============================================================

  isAuthenticated(): boolean {

    return !!this.token();

  }


  // ============================================================
  // GET CURRENT USER ROLE FROM JWT
  // ============================================================

  getCurrentUserRole(): string | null {

    const token = this.token();

    if (!token) {
      return null;
    }


    try {

      const parts = token.split('.');

      if (parts.length !== 3) {
        return null;
      }


      const base64Payload = parts[1]
        .replace(/-/g, '+')
        .replace(/_/g, '/');


      const paddedPayload =
        base64Payload +
        '='.repeat(
          (4 - base64Payload.length % 4) % 4
        );


      const payload = JSON.parse(
        atob(paddedPayload)
      );


      return payload.role ?? null;

    } catch (error) {

      console.error(
        'Unable to read role from JWT:',
        error
      );

      return null;

    }

  }


  // ============================================================
  // GET CURRENT USER
  // ============================================================

  currentUser(): User | null {

    /*
     * First try the complete user profile stored
     * in localStorage.
     */
    const raw = localStorage.getItem(
      'contractiq_user'
    );


    if (raw) {

      try {

        return JSON.parse(raw) as User;

      } catch {

        localStorage.removeItem(
          'contractiq_user'
        );

      }

    }


    /*
     * If the complete profile isn't available,
     * read basic information from the JWT.
     */
    const token = this.token();

    if (!token) {
      return null;
    }


    try {

      const parts = token.split('.');

      if (parts.length !== 3) {
        return null;
      }


      const base64Payload = parts[1]
        .replace(/-/g, '+')
        .replace(/_/g, '/');


      const paddedPayload =
        base64Payload +
        '='.repeat(
          (4 - base64Payload.length % 4) % 4
        );


      const payload = JSON.parse(
        atob(paddedPayload)
      );


      if (!payload.role) {
        return null;
      }


      return {
        id: Number(payload.sub),
        role: payload.role
      } as User;


    } catch (error) {

      console.error(
        'Unable to read current user from JWT:',
        error
      );

      return null;

    }

  }


  // ============================================================
  // STORE COMPLETE USER PROFILE
  // ============================================================

  setCurrentUser(user: User): void {

    localStorage.setItem(
      'contractiq_user',
      JSON.stringify(user)
    );

  }

}
