import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { LoginComponent } from './login/login.component';
import { ShellComponent } from './shell/shell.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { PlaceholderComponent } from './placeholder/placeholder.component';

export const routes: Routes = [
	{ path: 'login', component: LoginComponent },
	{ path: '', component: ShellComponent, canActivate: [authGuard], children: [
		{ path: '', pathMatch: 'full', redirectTo: 'dashboard' },
		{ path: 'dashboard', component: DashboardComponent },
		...['contracts', 'obligations', 'renewals', 'compliance', 'notifications', 'reports', 'audit'].map((path) => ({ path, component: PlaceholderComponent, data: { title: path === 'audit' ? 'Audit history' : path[0].toUpperCase() + path.slice(1) } })),
	] },
	{ path: '**', redirectTo: 'dashboard' },
];
