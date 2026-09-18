import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { User } from '../models/models';

export interface CreateUserPayload {
  email: string;
  password: string;
  full_name?: string;
  role: string;
}

export interface UpdateUserPayload {
  email?: string;
  password?: string;
  full_name?: string;
  role?: string;
  is_active?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    `${environment.apiUrl}/users`;

  list(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl);
  }

  get(id: number): Observable<User> {
    return this.http.get<User>(
      `${this.apiUrl}/${id}`
    );
  }

  create(
    payload: CreateUserPayload
  ): Observable<User> {

    return this.http.post<User>(
      this.apiUrl,
      payload
    );
  }

  update(
    id: number,
    payload: UpdateUserPayload
  ): Observable<User> {

    return this.http.put<User>(
      `${this.apiUrl}/${id}`,
      payload
    );
  }

  delete(id: number): Observable<void> {

    return this.http.delete<void>(
      `${this.apiUrl}/${id}`
    );
  }
}