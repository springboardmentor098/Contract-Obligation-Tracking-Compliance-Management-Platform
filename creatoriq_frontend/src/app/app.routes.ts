import { Routes } from '@angular/router';

import { Dashboard } from './pages/dashboard/dashboard';
import { Login } from './pages/login/login';
import { ForgotPassword } from './pages/forgot-password/forgot-password';
import { Contracts } from './pages/contracts/contracts';
import { Obligations } from './pages/obligations/obligations';
import { Renewals } from './pages/renewals/renewals';
import { Compliance } from './pages/compliance/compliance';
import { Notifications } from './pages/notifications/notifications';
import { Reports } from './pages/reports/reports';
import { AuditHistory } from './pages/audit-history/audit-history';

import { Layout } from './components/layout/layout';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [

  {
    path: 'login',
    component: Login
  },

  {
    path: 'forgot-password',
    component: ForgotPassword
  },

  {
    path: '',
    component: Layout,
    canActivate: [authGuard],

    children: [

      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },

      {
        path: 'dashboard',
        component: Dashboard
      },

      {
        path: 'contracts',
        component: Contracts
      },

      {
        path: 'obligations',
        component: Obligations
      },

      {
        path: 'renewals',
        component: Renewals
      },

      {
        path: 'compliance',
        component: Compliance
      },

      {
        path: 'notifications',
        component: Notifications
      },

      {
        path: 'reports',
        component: Reports
      },

      {
        path: 'audit-history',
        component: AuditHistory
      }

    ]
  },

  {
    path: '**',
    redirectTo: ''
  }

];