import { Injectable, inject } from '@angular/core';
import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders,
  HttpParams
} from '@angular/common/http';

import {
  Observable,
  catchError,
  throwError,
  tap
} from 'rxjs';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://127.0.0.1:8000';

  login(username: string, password: string): Observable<LoginResponse> {

    const body = new HttpParams()
      .set('username', username.trim())
      .set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http
      .post<LoginResponse>(
        `${this.apiUrl}/auth/login`,
        body.toString(),
        { headers }
      )
      .pipe(

        tap((response) => {

          console.log('Login response received:', response);

          if (response?.access_token) {

            localStorage.setItem(
              'access_token',
              response.access_token
            );

            localStorage.setItem(
              'token_type',
              response.token_type || 'bearer'
            );

            console.log(
              'Token saved:',
              localStorage.getItem('access_token')
            );

          } else {

            console.error(
              'Login succeeded but access_token is missing.'
            );
          }
        }),

        catchError((error: HttpErrorResponse) => {

          console.error(
            'AuthService login error:',
            error
          );

          this.logout();

          return throwError(() => error);
        })
      );
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getTokenType(): string {
    return localStorage.getItem('token_type') || 'bearer';
  }

  isLoggedIn(): boolean {

    const token = this.getToken();

    return !!token && token.trim().length > 0;
  }

  logout(): void {

    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
  }
}