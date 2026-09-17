import { Routes } from '@angular/router';

import { Layout } from './layout/layout';
import { Dashboard } from './pages/dashboard/dashboard';
import { Contracts } from './pages/contracts/contracts';
import { Obligations } from './pages/obligations/obligations';
import { Renewals } from './pages/renewals/renewals';
import { RenewalMonitoring } from './pages/renewal-monitoring/renewal-monitoring';
import { Compliance } from './pages/compliance/compliance';
import { Notifications } from './pages/notifications/notifications';
import { Reports } from './pages/reports/reports';
import { AuditHistory } from './pages/audit-history/audit-history';
import { Login } from './pages/login/login';
import { Register } from './pages/register/register';
import { ForgotPassword } from './pages/forgot-password/forgot-password';
import { authGuard } from './guards/auth.guard';

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
    path: 'register',
    component: Register
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
        path: 'renewal-monitoring',
        component: RenewalMonitoring
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
    redirectTo: 'login'
  }
];
