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

  isAdmin(): boolean {
    return this.role === 'Administrator' || this.role === 'Admin';
  }

  isContractManager(): boolean {
    return this.role === 'Contract Manager';
  }

  isComplianceOfficer(): boolean {
    return this.role === 'Compliance Officer';
  }

  isViewer(): boolean {
    return this.role === 'Viewer';
  }
}