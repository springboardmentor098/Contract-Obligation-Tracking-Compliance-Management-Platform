import { Component, inject } from '@angular/core';
import {
  RouterLink,
  RouterLinkActive
} from '@angular/router';

import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';

import {
  AuthService,
  UserRole
} from '../../services/auth.service';

interface NavigationItem {
  label: string;
  icon: string;
  route: string;
  roles: UserRole[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    MatListModule,
    MatIconModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent {

  private readonly authService = inject(AuthService);

  readonly navigationItems: NavigationItem[] = [

    {
      label: 'Dashboard',
      icon: 'dashboard',
      route: '/dashboard',
      roles: [
        UserRole.ADMINISTRATOR,
        UserRole.LEGAL_MANAGER,
        UserRole.COMPLIANCE_OFFICER,
        UserRole.CONTRACT_MANAGER,
        UserRole.DEPARTMENT_HEAD,
        UserRole.EMPLOYEE
      ]
    },

    {
      label: 'Contracts',
      icon: 'description',
      route: '/contracts',
      roles: [
        UserRole.ADMINISTRATOR,
        UserRole.LEGAL_MANAGER,
        UserRole.COMPLIANCE_OFFICER,
        UserRole.CONTRACT_MANAGER,
        UserRole.DEPARTMENT_HEAD,
        UserRole.EMPLOYEE
      ]
    },

    {
      label: 'Obligations',
      icon: 'task',
      route: '/obligations',
      roles: [
        UserRole.ADMINISTRATOR,
        UserRole.LEGAL_MANAGER,
        UserRole.COMPLIANCE_OFFICER,
        UserRole.CONTRACT_MANAGER,
        UserRole.DEPARTMENT_HEAD,
        UserRole.EMPLOYEE
      ]
    },

    {
      label: 'Renewals',
      icon: 'event',
      route: '/renewals',
      roles: [
        UserRole.ADMINISTRATOR,
        UserRole.CONTRACT_MANAGER
      ]
    },

    {
      label: 'Compliance',
      icon: 'verified',
      route: '/compliance',
      roles: [
        UserRole.ADMINISTRATOR,
        UserRole.COMPLIANCE_OFFICER
      ]
    },

    {
      label: 'Notifications',
      icon: 'notifications',
      route: '/notifications',
      roles: [
        UserRole.ADMINISTRATOR,
        UserRole.LEGAL_MANAGER,
        UserRole.COMPLIANCE_OFFICER,
        UserRole.CONTRACT_MANAGER,
        UserRole.DEPARTMENT_HEAD,
        UserRole.EMPLOYEE
      ]
    },

    {
      label: 'Reports',
      icon: 'bar_chart',
      route: '/reports',
      roles: [
        UserRole.ADMINISTRATOR,
        UserRole.LEGAL_MANAGER,
        UserRole.COMPLIANCE_OFFICER,
        UserRole.DEPARTMENT_HEAD
      ]
    },

    {
      label: 'Audit History',
      icon: 'history',
      route: '/audit-history',
      roles: [
        UserRole.ADMINISTRATOR,
        UserRole.COMPLIANCE_OFFICER
      ]
    }
  ];

  isAllowed(item: NavigationItem): boolean {
    return this.authService.hasAnyRole(item.roles);
  }

  get currentRole(): string {
    return this.authService.getRole() ?? 'User';
  }
}