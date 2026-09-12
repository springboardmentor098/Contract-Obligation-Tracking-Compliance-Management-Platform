import { Routes } from '@angular/router';

import { Dashboard } from './dashboard/dashboard';
import { Login } from './login/login';
import { Layout } from './layout/layout';

import { Contracts } from './contracts/contracts';
import { Obligations } from './obligations/obligations';
import { Renewals } from './renewals/renewals';
import { Compliance } from './compliance/compliance';
import { Notifications } from './notifications/notifications';
import { Reports } from './reports/reports';
import { AuditHistory } from './audit-history/audit-history';

import { authGuard } from './guards/auth-guard';


export const routes: Routes = [

  // =========================
  // Default Route
  // =========================

  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },


  // =========================
  // Login
  // =========================

  {
    path: 'login',
    component: Login
  },


  // =========================
  // Protected Application
  // =========================

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


  // =========================
  // Unknown Route
  // =========================

  {
    path: '**',
    redirectTo: 'login'
  }

];