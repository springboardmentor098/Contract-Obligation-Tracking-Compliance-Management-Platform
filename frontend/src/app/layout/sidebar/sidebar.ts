import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

interface NavigationItem {
  label: string;
  route: string;
  roles: string[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class Sidebar {
  private readonly authService = inject(AuthService);

  private readonly navigationItems: NavigationItem[] = [
    {
      label: 'Dashboard',
      route: '/dashboard',
      roles: [
        'Administrator',
        'Legal Manager',
        'Compliance Officer',
        'Contract Manager',
        'Department Head',
        'Employee'
      ]
    },
    {
      label: 'Contracts',
      route: '/contracts',
      roles: [
        'Administrator',
        'Legal Manager',
        'Contract Manager'
      ]
    },
    {
      label: 'Obligations',
      route: '/obligations',
      roles: [
        'Administrator'
      ]
    },
    {
      label: 'Renewals',
      route: '/renewals',
      roles: [
        'Administrator'
      ]
    },
    {
      label: 'Compliance',
      route: '/compliance',
      roles: [
        'Administrator',
        'Compliance Officer'
      ]
    },
    {
      label: 'Notifications',
      route: '/notifications',
      roles: [
        'Administrator'
      ]
    },
    {
      label: 'Reports & Analytics',
      route: '/reports',
      roles: [
        'Administrator'
      ]
    },
    {
      label: 'Audit History',
      route: '/audit',
      roles: [
        'Administrator'
      ]
    }
  ];

  get role(): string {
    return this.authService.getRole() ?? '';
  }

  get workspaceItems(): NavigationItem[] {
    return this.navigationItems
      .filter(item =>
        ['Dashboard', 'Contracts', 'Obligations', 'Renewals', 'Compliance']
          .includes(item.label)
      )
      .filter(item => item.roles.includes(this.role));
  }

  get insightItems(): NavigationItem[] {
    return this.navigationItems
      .filter(item =>
        ['Notifications', 'Reports & Analytics', 'Audit History']
          .includes(item.label)
      )
      .filter(item => item.roles.includes(this.role));
  }
}
