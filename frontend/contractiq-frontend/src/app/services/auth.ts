import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

interface LoginResponse {
  access_token: string;
  token_type: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class Auth {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<LoginResponse> {

    const body = new URLSearchParams();

    body.set('grant_type', 'password');
    body.set('username', username);
    body.set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http.post<LoginResponse>(
      `${this.apiUrl}/login`,
      body.toString(),
      { headers }
    );
  }

  saveToken(response: LoginResponse): void {
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('token_type', response.token_type);
    localStorage.setItem('role', response.role);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('role');
  }
}
