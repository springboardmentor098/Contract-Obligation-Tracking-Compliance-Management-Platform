import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css'
})
export class Sidebar {

  role: string | null = null;

  constructor(private authService: AuthService) {
    this.role = this.authService.getRole();
  }

  private normalizedRole(): string {
    return (this.role || '').trim().toLowerCase();
  }

  isAdmin(): boolean {
    const role = this.normalizedRole();
    return role === 'administrator' || role === 'admin';
  }

  isContractManager(): boolean {
    return this.normalizedRole() === 'contract manager';
  }

  isComplianceOfficer(): boolean {
    return this.normalizedRole() === 'compliance officer';
  }

  isViewer(): boolean {
    return this.normalizedRole() === 'viewer';
  }

  isEmployee(): boolean {
    return this.normalizedRole() === 'employee';
  }
}
