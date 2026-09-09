import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({ selector: 'app-shell', standalone: true, imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet], templateUrl: './shell.component.html', styleUrl: './shell.component.scss' })
export class ShellComponent {
  readonly auth = inject(AuthService); menuOpen = false;
  readonly navigation = [{ label: 'Dashboard', icon: '01', path: '/dashboard' }, { label: 'Contracts', icon: '02', path: '/contracts' }, { label: 'Obligations', icon: '03', path: '/obligations' }, { label: 'Renewals', icon: '04', path: '/renewals' }, { label: 'Compliance', icon: '05', path: '/compliance' }, { label: 'Notifications', icon: '06', path: '/notifications' }, { label: 'Reports', icon: '07', path: '/reports' }, { label: 'Audit history', icon: '08', path: '/audit' }];
}