import { Routes } from '@angular/router';
import { authGuard, roleGuard } from './core/auth.guard';
import { ShellComponent } from './layout/shell.component';
import { LoginComponent } from './pages/auth/login.component';
import { RegisterComponent } from './pages/auth/register.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { ContractListComponent } from './pages/contracts/contract-list.component';
import { ContractFormComponent } from './pages/contracts/contract-form.component';
import { ContractDetailComponent } from './pages/contracts/contract-detail.component';
import { ObligationListComponent } from './pages/obligations/obligation-list.component';
import { ObligationFormComponent } from './pages/obligations/obligation-form.component';
import { RenewalListComponent } from './pages/renewals/renewal-list.component';
import { ComplianceComponent } from './pages/compliance/compliance.component';
import { NotificationsComponent } from './pages/notifications/notifications.component';
import { ReportsComponent } from './pages/reports/reports.component';
import { UsersComponent } from './pages/users/users.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'contracts', component: ContractListComponent },
      { path: 'contracts/new', component: ContractFormComponent },
      { path: 'contracts/:id/edit', component: ContractFormComponent },
      { path: 'contracts/:id', component: ContractDetailComponent },
      { path: 'obligations', component: ObligationListComponent },
      { path: 'obligations/new', component: ObligationFormComponent },
      { path: 'renewals', component: RenewalListComponent },
      { path: 'compliance', component: ComplianceComponent },
      { path: 'reports', component: ReportsComponent },
      { path: 'notifications', component: NotificationsComponent },
      { path: 'users', component: UsersComponent, canActivate: [roleGuard('Administrator')] },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
