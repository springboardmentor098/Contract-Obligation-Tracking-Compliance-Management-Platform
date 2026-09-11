import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { LayoutComponent } from './layout/layout.component';
import { LoginComponent } from './features/auth/login.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { ContractsComponent } from './features/contracts/contracts.component';
import { ObligationsComponent } from './features/obligations/obligations.component';
import { RenewalsComponent } from './features/renewals/renewals.component';
import { ComplianceComponent } from './features/compliance/compliance.component';
import { NotificationsComponent } from './features/notifications/notifications.component';
import { ReportsComponent } from './features/reports/reports.component';
import { AuditComponent } from './features/audit/audit.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'contracts', component: ContractsComponent },
      { path: 'obligations', component: ObligationsComponent },
      { path: 'renewals', component: RenewalsComponent },
      { path: 'compliance', component: ComplianceComponent },
      { path: 'notifications', component: NotificationsComponent },
      { path: 'reports', component: ReportsComponent },
      { path: 'audit', component: AuditComponent }
    ]
  },
  { path: '**', redirectTo: 'dashboard' }
];
