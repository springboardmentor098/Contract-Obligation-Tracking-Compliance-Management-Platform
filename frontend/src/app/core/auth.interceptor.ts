import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('contractiq_token');
  const router = inject(Router);
  const authedReq = token
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(authedReq).pipe(
    catchError(err => {
      if (err.status === 401) {
        localStorage.removeItem('contractiq_token');
        localStorage.removeItem('contractiq_user');
        router.navigate(['/login']);
      }
      return throwError(() => err);
    })
  );
};
