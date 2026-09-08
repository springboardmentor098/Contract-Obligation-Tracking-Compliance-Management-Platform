import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('access_token');

  console.log('Auth interceptor token:', token ? 'TOKEN FOUND' : 'NO TOKEN');

  if (token) {
    const authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });

    console.log('Authorization header added');

    return next(authReq);
  }

  return next(req);
};