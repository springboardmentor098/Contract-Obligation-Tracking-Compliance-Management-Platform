import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../core/auth.service';
import { NotificationsService } from '../core/data.service';
import { UserRole } from '../core/models';

interface NavItem { label: string; path: string; roles?: UserRole[]; }

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  template: `
  <div class="shell">
    <aside class="rail">
      <div class="brand">
        <span class="brand-mark">CIQ</span>
        <div>
          <strong>ContractIQ</strong>
          <small>Obligation &amp; Compliance Register</small>
        </div>
      </div>
      <nav>
        <a *ngFor="let item of visibleNav()" [routerLink]="item.path" routerLinkActive="active" class="nav-item">
          {{ item.label }}
        </a>
      </nav>
      <div class="rail-foot">
        <div class="who">
          <strong>{{ auth.user()?.full_name }}</strong>
          <small>{{ auth.user()?.role }}</small>
        </div>
        <button class="btn-ghost btn-sm" (click)="auth.logout()">Sign out</button>
      </div>
    </aside>

    <div class="main-col">
      <header class="topbar">
        <span class="docket-num">{{ today }}</span>
        <a routerLink="/notifications" class="bell" [class.has-unread]="unreadCount() > 0">
          Notifications
          <span *ngIf="unreadCount() > 0" class="badge">{{ unreadCount() }}</span>
        </a>
      </header>
      <main class="content"><router-outlet /></main>
    </div>
  </div>
  `,
  styles: [`
    .shell { display: flex; min-height: 100vh; }
    .rail {
      width: 232px; flex-shrink: 0; background: var(--ink); color: #DDE4EA;
      display: flex; flex-direction: column; position: sticky; top: 0; height: 100vh;
    }
    .brand { display: flex; align-items: center; gap: 10px; padding: 22px 18px 18px; border-bottom: 1px solid #2B3F5A; }
    .brand-mark {
      font-family: var(--font-mono); font-size: 12px; font-weight: 500; color: var(--ink);
      background: #C9D3D0; border-radius: 3px; padding: 4px 6px; letter-spacing: .03em;
    }
    .brand strong { display: block; font-family: var(--font-display); font-size: 16.5px; color: #fff; }
    .brand small { display: block; font-size: 11px; color: #8FA0B3; margin-top: 1px; }
    nav { display: flex; flex-direction: column; padding: 14px 10px; gap: 2px; flex: 1; overflow-y: auto; }
    .nav-item {
      display: block; text-decoration: none; color: #B7C2CE; font-size: 14px; padding: 9px 12px;
      border-radius: 3px; border-left: 2px solid transparent;
    }
    .nav-item:hover { background: #1F3654; color: #fff; }
    .nav-item.active { background: #1F3654; color: #fff; border-left-color: var(--seal); font-weight: 500; }
    .rail-foot { padding: 14px 16px 18px; border-top: 1px solid #2B3F5A; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .who strong { display: block; font-size: 13px; color: #fff; }
    .who small { display: block; font-size: 11.5px; color: #8FA0B3; }
    .rail-foot .btn-ghost { border-color: #3A4F6B; color: #DDE4EA; }
    .rail-foot .btn-ghost:hover { background: #1F3654; }

    .main-col { flex: 1; min-width: 0; display: flex; flex-direction: column; }
    .topbar {
      display: flex; justify-content: space-between; align-items: center;
      padding: 14px 32px; border-bottom: 1px solid var(--line); background: var(--surface);
    }
    .bell { text-decoration: none; color: var(--ink-soft); font-size: 13.5px; display: flex; align-items: center; gap: 7px; }
    .bell.has-unread { color: var(--ink); font-weight: 500; }
    .badge { background: var(--rose); color: #fff; font-size: 11px; border-radius: 100px; padding: 1px 7px; font-family: var(--font-mono); }
    .content { padding: 28px 32px 60px; max-width: 1180px; width: 100%; margin: 0 auto; }
  `],
})
export class ShellComponent implements OnInit {
  auth = inject(AuthService);
  private notificationsService = inject(NotificationsService);
  unreadCount = signal(0);
  today = new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  private allNav: NavItem[] = [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Contracts', path: '/contracts' },
    { label: 'Obligations', path: '/obligations' },
    { label: 'Renewals', path: '/renewals' },
    { label: 'Compliance', path: '/compliance' },
    { label: 'Reports', path: '/reports' },
    { label: 'Notifications', path: '/notifications' },
    { label: 'Users', path: '/users', roles: ['Administrator'] },
  ];

  visibleNav() {
    return this.allNav.filter(i => !i.roles || this.auth.hasRole(...i.roles));
  }

  ngOnInit() {
    if (!this.auth.user()) this.auth.fetchMe().subscribe();
    this.notificationsService.list().subscribe(list => {
      this.unreadCount.set(list.filter(n => n.status === 'Unread').length);
    });
  }
}
