import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const router = inject(Router);
  const token = localStorage.getItem('contractiq_access_token');
  const authorizedRequest = token ? request.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : request;
  return next(authorizedRequest).pipe(catchError((error) => {
    if (error.status === 401) {
      localStorage.removeItem('contractiq_access_token');
      localStorage.removeItem('contractiq_user');
      void router.navigate(['/login'], { queryParams: { reason: 'expired' } });
    }
    return throwError(() => error);
  }));
};