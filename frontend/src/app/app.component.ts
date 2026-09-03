import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

interface Dashboard { contracts: any; obligations: any; renewals: any; compliance: any; }

@Component({selector: 'app-root', standalone: true, imports: [CommonModule], templateUrl: './app.component.html'})
export class AppComponent {
  private http = inject(HttpClient);
  api = 'http://localhost:8000';
  data: Dashboard | null = null;
  error = '';

  ngOnInit() {
    const token = localStorage.getItem('contractiq_token');
    const headers = token ? {Authorization: `Bearer ${token}`} : {};
    this.http.get<Dashboard>(`${this.api}/dashboard/summary`, {headers}).subscribe({next: v => this.data = v, error: e => this.error = e.status === 401 ? 'Please sign in to view the dashboard.' : 'Unable to load dashboard data.'});
  }

  download(kind: string, fmt: string) {
    const token = localStorage.getItem('contractiq_token');
    const headers = token ? {Authorization: `Bearer ${token}`} : {};
    this.http.get(`${this.api}/reports/${kind}/export/${fmt}`, {headers, responseType: 'blob'}).subscribe(blob => {
      const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `contractiq_${kind}_report.${fmt === 'excel' ? 'xlsx' : 'pdf'}`; a.click(); URL.revokeObjectURL(url);
    });
  }
}
