import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Obligation {
  id: number;
  contract_id: number;
  title: string;
  description: string | null;
  obligation_type: string;
  due_date: string;
  assigned_to: number;
  status: string;
  progress: number;
  completion_date: string | null;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class Obligations {

  private readonly baseUrl = 'http://127.0.0.1:8000/obligations';

  constructor(private http: HttpClient) {}

  getObligations(): Observable<Obligation[]> {
    return this.http.get<Obligation[]>(this.baseUrl);
  }
}