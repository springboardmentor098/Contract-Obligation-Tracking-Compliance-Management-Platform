import { Routes } from '@angular/router';

import { MainLayout } from './layout/main-layout/main-layout';

import { Dashboard } from './pages/dashboard/dashboard';
import { Contracts } from './pages/contracts/contracts';
import { ContractDetails } from './pages/contract-details/contract-details';
import { Obligations } from './pages/obligations/obligations';
import { Renewals } from './pages/renewals/renewals';
import { Compliance } from './pages/compliance/compliance';
import { Notifications } from './pages/notifications/notifications';
import { Reports } from './pages/reports/reports';
import { Audit } from './pages/audit/audit';
import { Login } from './pages/login/login';

import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [

  {
    path: 'login',
    component: Login
  },

  {
    path: '',
    component: MainLayout,
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
        component: Contracts,
        canActivate: [
          roleGuard([
            'Administrator',
            'Legal Manager',
            'Contract Manager'
          ])
        ]
      },

      {
        path: 'contracts/:id',
        component: ContractDetails,
        canActivate: [
          roleGuard([
            'Administrator',
            'Legal Manager',
            'Contract Manager'
          ])
        ]
      },

      {
        path: 'obligations',
        component: Obligations,
        canActivate: [
          roleGuard(['Administrator'])
        ]
      },

      {
        path: 'renewals',
        component: Renewals,
        canActivate: [
          roleGuard(['Administrator'])
        ]
      },

      {
        path: 'compliance',
        component: Compliance,
        canActivate: [
          roleGuard([
            'Administrator',
            'Compliance Officer'
          ])
        ]
      },

      {
        path: 'notifications',
        component: Notifications,
        canActivate: [
          roleGuard(['Administrator'])
        ]
      },

      {
        path: 'reports',
        component: Reports,
        canActivate: [
          roleGuard(['Administrator'])
        ]
      },

      {
        path: 'audit',
        component: Audit,
        canActivate: [
          roleGuard(['Administrator'])
        ]
      }

    ]
  },

  {
    path: '**',
    redirectTo: 'dashboard'
  }

];
