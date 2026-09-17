import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<LoginResponse> {
  const body = new URLSearchParams();
  body.set('username', email);
  body.set('password', password);

  return this.http.post<LoginResponse>(
    `${this.apiUrl}/auth/login`,
    body.toString(),
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }
  ).pipe(
    tap(response => {
      localStorage.setItem('access_token', response.access_token);
    })
  );
}
getRole(): string | null {
  const token = this.getToken();

  if (!token) {
    return null;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.role || null;
  } catch {
    return null;
  }
}
getUserId(): string | null {
  const token = this.getToken();

  if (!token) {
    return null;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.sub || null;
  } catch {
    return null;
  }
}
getUserEmail(): string | null {
  const token = this.getToken();

  if (!token) {
    return null;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));

    return payload.sub || null;
  } catch {
    return null;
  }
}

  logout(): void {
    localStorage.removeItem('access_token');
  }

isLoggedIn(): boolean {
  const token = this.getToken();

  if (!token) {
    return false;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));

    if (!payload.exp) {
      return true;
    }

    const currentTime = Math.floor(Date.now() / 1000);

    if (payload.exp <= currentTime) {
      this.logout();
      return false;
    }

    return true;
  } catch {
    this.logout();
    return false;
  }
}

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}
