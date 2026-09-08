import { Routes } from '@angular/router';

import { Login } from './auth/login/login';
import { ForgotPassword } from './auth/forgot-password/forgot-password';

import { Dashboard } from './dashboard/dashboard';
import { Contracts } from './contracts/contracts';
import { Obligations } from './obligations/obligations';
import { Renewals } from './renewals/renewals';
import { Compliance } from './compliance/compliance';
import { Notifications } from './notifications/notifications';
import { Reports } from './reports/reports';
import { AuditHistory } from './audit-history/audit-history';

import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },

  {
    path: 'login',
    component: Login
  },

  {
    path: 'forgot-password',
    component: ForgotPassword
  },

  {
    path: 'dashboard',
    component: Dashboard,
    canActivate: [authGuard]
  },

  {
    path: 'contracts',
    component: Contracts,
    canActivate: [authGuard]
  },

  {
    path: 'obligations',
    component: Obligations,
    canActivate: [authGuard]
  },

  {
    path: 'renewals',
    component: Renewals,
    canActivate: [authGuard]
  },

  {
    path: 'compliance',
    component: Compliance,
    canActivate: [authGuard]
  },

  {
    path: 'notifications',
    component: Notifications,
    canActivate: [authGuard]
  },

  {
    path: 'reports',
    component: Reports,
    canActivate: [authGuard]
  },

  {
    path: 'audit-history',
    component: AuditHistory,
    canActivate: [authGuard]
  },

  {
    path: '**',
    redirectTo: 'login'
  }
];