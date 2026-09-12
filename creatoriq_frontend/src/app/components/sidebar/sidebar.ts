import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css'
})
export class Sidebar {

  constructor(private auth: Auth) {}

  get role(): string | null {
    return this.auth.getRole();
  }

  canViewContracts(): boolean {
    return (
      this.role === 'Administrator' ||
      this.role === 'Legal Manager' ||
      this.role === 'Contract Manager'
    );
  }

  canViewObligations(): boolean {
    return (
      this.role === 'Administrator' ||
      this.role === 'Compliance Officer' ||
      this.role === 'Department Head'
    );
  }

  canViewRenewals(): boolean {
    return (
      this.role === 'Administrator' ||
      this.role === 'Legal Manager' ||
      this.role === 'Contract Manager'
    );
  }

  canViewReports(): boolean {
    return true;
  }

  canViewAuditHistory(): boolean {
    return (
      this.role === 'Administrator' ||
      this.role === 'Compliance Officer'
    );
  }
}