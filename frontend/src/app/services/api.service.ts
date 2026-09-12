import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiBaseUrl;

  list<T>(path: string, params?: Record<string, string | number>): Observable<T> {
    let httpParams = new HttpParams();
    Object.entries(params ?? {}).forEach(([key, value]) => httpParams = httpParams.set(key, String(value)));
    return this.http.get<T>(`${this.base}${path}`, { params: httpParams });
  }

  create<T>(path: string, body: unknown): Observable<T> { return this.http.post<T>(`${this.base}${path}`, body); }
  update<T>(path: string, body: unknown): Observable<T> { return this.http.put<T>(`${this.base}${path}`, body); }
  patch<T>(path: string, body?: unknown): Observable<T> { return this.http.patch<T>(`${this.base}${path}`, body ?? {}); }
  remove<T>(path: string): Observable<T> { return this.http.delete<T>(`${this.base}${path}`); }
  download(path: string): Observable<Blob> { return this.http.get(`${this.base}${path}`, { responseType: 'blob' }); }
}
