import { inject } from '@angular/core';

import {
  CanActivateFn,
  Router
} from '@angular/router';

import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {

  const authService = inject(AuthService);
  const router = inject(Router);

  const token = authService.getToken();

  console.log(
    'Auth Guard - token exists:',
    !!token
  );

  if (token && token.trim().length > 0) {

    return true;
  }

  console.log(
    'Auth Guard - no token, redirecting to login.'
  );

  return router.createUrlTree([
    '/login'
  ]);
};