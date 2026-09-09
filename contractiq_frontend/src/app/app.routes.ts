import { Routes } from '@angular/router';

import { Layout } from './layout/layout';
import { Dashboard } from './dashboard/dashboard';
import { Contracts } from './contracts/contracts';
import { Obligations } from './obligations/obligations';
import { Renewals } from './renewals/renewals';
import { Compliance } from './compliance/compliance';
import { Notifications } from './notifications/notifications';
import { Reports } from './reports/reports';
import { AuditHistory } from './audit-history/audit-history';
import { Login } from './auth/login/login';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  {
    path: 'login',
    component: Login
  },
  {
    path: '',
    component: Layout,
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: Dashboard, canActivate: [authGuard] },
      { path: 'contracts', component: Contracts, canActivate: [authGuard] },
      { path: 'obligations', component: Obligations, canActivate: [authGuard] },
      { path: 'renewals', component: Renewals, canActivate: [authGuard] },
      { path: 'compliance', component: Compliance, canActivate: [authGuard] },
      { path: 'notifications', component: Notifications, canActivate: [authGuard] },
      { path: 'reports', component: Reports, canActivate: [authGuard] },
      { path: 'audit-history', component: AuditHistory, canActivate: [authGuard] }
    ]
  }
];