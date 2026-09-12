import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Renewal {
  id: number;
  contract_id: number;
  renewal_date: string;
  previous_expiry_date: string;
  new_expiry_date: string;
  status: string;
  assigned_to: number;
  approval_status: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class Renewals {

  private readonly baseUrl = 'http://127.0.0.1:8000/renewals';

  constructor(private http: HttpClient) {}

  getRenewals(): Observable<Renewal[]> {
    return this.http.get<Renewal[]>(this.baseUrl);
  }
}