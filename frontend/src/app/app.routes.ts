import { Routes } from '@angular/router';

import { LayoutComponent } from './layout/layout.component';

import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { ContractsComponent } from './pages/contracts/contracts.component';
import { ObligationsComponent } from './pages/obligations/obligations.component';
import { RenewalsComponent } from './pages/renewals/renewals.component';
import { ComplianceComponent } from './pages/compliance/compliance.component';
import { NotificationsComponent } from './pages/notifications/notifications.component';
import { ReportsComponent } from './pages/reports/reports.component';
import { AuditHistoryComponent } from './pages/audit-history/audit-history.component';

import { LoginComponent } from './pages/login/login.component';
import { ForgotPasswordComponent } from './pages/forgot-password/forgot-password.component';

import {
  authGuard,
  roleGuard
} from './guards/auth.guard';

import { UserRole } from './services/auth.service';

export const routes: Routes = [

  // ============================================================
  // PUBLIC AUTHENTICATION ROUTES
  // ============================================================

  {
    path: 'login',
    component: LoginComponent
  },

  {
    path: 'forgot-password',
    component: ForgotPasswordComponent
  },

  // ============================================================
  // AUTHENTICATED APPLICATION
  // ============================================================

  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],

    children: [

      // Default route
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },

      // ========================================================
      // DASHBOARD
      // All authenticated roles can access
      // ========================================================

      {
        path: 'dashboard',
        component: DashboardComponent
      },

      // ========================================================
      // CONTRACTS
      // All roles have contracts:read permission
      // ========================================================

      {
        path: 'contracts',
        component: ContractsComponent,
        canActivate: [
          roleGuard([
            UserRole.ADMINISTRATOR,
            UserRole.LEGAL_MANAGER,
            UserRole.COMPLIANCE_OFFICER,
            UserRole.CONTRACT_MANAGER,
            UserRole.DEPARTMENT_HEAD,
            UserRole.EMPLOYEE
          ])
        ]
      },

      // ========================================================
      // OBLIGATIONS
      // All roles have obligations:read permission
      // ========================================================

      {
        path: 'obligations',
        component: ObligationsComponent,
        canActivate: [
          roleGuard([
            UserRole.ADMINISTRATOR,
            UserRole.LEGAL_MANAGER,
            UserRole.COMPLIANCE_OFFICER,
            UserRole.CONTRACT_MANAGER,
            UserRole.DEPARTMENT_HEAD,
            UserRole.EMPLOYEE
          ])
        ]
      },

      // ========================================================
      // RENEWALS
      // Administrator + Contract Manager
      // ========================================================

      {
        path: 'renewals',
        component: RenewalsComponent,
        canActivate: [
          roleGuard([
            UserRole.ADMINISTRATOR,
            UserRole.CONTRACT_MANAGER
          ])
        ]
      },

      // ========================================================
      // COMPLIANCE
      // Administrator + Compliance Officer
      // ========================================================

      {
        path: 'compliance',
        component: ComplianceComponent,
        canActivate: [
          roleGuard([
            UserRole.ADMINISTRATOR,
            UserRole.COMPLIANCE_OFFICER
          ])
        ]
      },

      // ========================================================
      // NOTIFICATIONS
      // All authenticated roles
      // ========================================================

      {
        path: 'notifications',
        component: NotificationsComponent,
        canActivate: [
          roleGuard([
            UserRole.ADMINISTRATOR,
            UserRole.LEGAL_MANAGER,
            UserRole.COMPLIANCE_OFFICER,
            UserRole.CONTRACT_MANAGER,
            UserRole.DEPARTMENT_HEAD,
            UserRole.EMPLOYEE
          ])
        ]
      },

      // ========================================================
      // REPORTS
      // Administrator + Legal Manager +
      // Compliance Officer + Department Head
      // ========================================================

      {
        path: 'reports',
        component: ReportsComponent,
        canActivate: [
          roleGuard([
            UserRole.ADMINISTRATOR,
            UserRole.LEGAL_MANAGER,
            UserRole.COMPLIANCE_OFFICER,
            UserRole.DEPARTMENT_HEAD
          ])
        ]
      },

      // ========================================================
      // AUDIT HISTORY
      // Administrator + Compliance Officer
      // ========================================================

      {
        path: 'audit-history',
        component: AuditHistoryComponent,
        canActivate: [
          roleGuard([
            UserRole.ADMINISTRATOR,
            UserRole.COMPLIANCE_OFFICER
          ])
        ]
      }

    ]
  },

  // ============================================================
  // UNKNOWN ROUTES
  // ============================================================

  {
    path: '**',
    redirectTo: 'dashboard'
  }

];
