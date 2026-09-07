import { Routes } from '@angular/router';
import { Dashboard } from './dashboard/dashboard';
import { Reports } from './reports/reports';

export const routes: Routes = [
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
    path: 'reports',
    component: Reports
  }
];