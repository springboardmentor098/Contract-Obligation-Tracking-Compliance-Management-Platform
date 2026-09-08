import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import {
  AuthService,
  UserRole
} from '../services/auth.service';

/**
 * Authentication guard
 *
 * Allows access only to logged-in users.
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return true;
  }

  return router.createUrlTree(['/login']);
};


/**
 * Role-based authorization guard
 *
 * Allows access only when the logged-in user's role
 * is included in the allowed roles for the route.
 */
export const roleGuard = (
  allowedRoles: UserRole[]
): CanActivateFn => {

  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);

    // First check authentication
    if (!authService.isLoggedIn()) {
      return router.createUrlTree(['/login']);
    }

    // Get current user's role
    const currentRole = authService.getRole();

    // Check whether the user's role is allowed
    if (
      currentRole &&
      allowedRoles.includes(currentRole as UserRole)
    ) {
      return true;
    }

    // User is logged in but does not have permission
    return router.createUrlTree(['/dashboard']);
  };
};