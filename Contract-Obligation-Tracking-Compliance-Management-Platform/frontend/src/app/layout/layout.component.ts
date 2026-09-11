import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../core/services/auth.service';

@Component({
  selector: 'cq-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.css'
})
export class LayoutComponent {
  readonly auth = inject(AuthService);
  sidebarOpen = true;

  nav = [
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    { label: 'Contracts', icon: 'description', route: '/contracts' },
    { label: 'Obligations', icon: 'task_alt', route: '/obligations' },
    { label: 'Renewals', icon: 'event_repeat', route: '/renewals' },
    { label: 'Compliance', icon: 'verified_user', route: '/compliance' },
    { label: 'Notifications', icon: 'notifications', route: '/notifications' },
    { label: 'Reports & Analytics', icon: 'bar_chart', route: '/reports' },
    { label: 'Audit / Activity', icon: 'history', route: '/audit' }
  ];

  toggleSidebar() { this.sidebarOpen = !this.sidebarOpen; }
}
