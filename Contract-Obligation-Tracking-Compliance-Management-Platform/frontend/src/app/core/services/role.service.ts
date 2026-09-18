import { Injectable, inject } from '@angular/core';

import { AuthService } from './auth.service';

import {
  UserRole,
  ROLE_PERMISSIONS
} from '../models/roles';

@Injectable({
  providedIn: 'root'
})
export class RoleService {

  private readonly auth = inject(AuthService);

  getRole(): string | null {
    return this.auth.getCurrentUserRole();
  }

  isAdmin(): boolean {
    return this.getRole() === UserRole.Administrator;
  }

  hasRole(role: string): boolean {
    return this.getRole() === role;
  }

  hasAnyRole(roles: string[]): boolean {
    const currentRole = this.getRole();

    return !!currentRole && roles.includes(currentRole);
  }

  hasPermission(permission: string): boolean {
    const role = this.getRole();

    if (!role) {
      return false;
    }

    return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
  }

  getPermissions(): string[] {
    const role = this.getRole();

    if (!role) {
      return [];
    }

    return ROLE_PERMISSIONS[role] ?? [];
  }
}