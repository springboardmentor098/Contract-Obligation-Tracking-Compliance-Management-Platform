import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { NotificationsService } from '../../core/data.service';
import { AppNotification } from '../../core/models';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
  <div class="page-head">
    <div>
      <h1>Notifications</h1>
      <p class="muted">Renewal reminders, obligation alerts, and approval notices.</p>
    </div>
    <button class="btn-ghost" *ngIf="unread().length" (click)="markAll()">Mark all as read</button>
  </div>

  <p class="error-banner" *ngIf="error()">{{ error() }}</p>

  <div class="panel" *ngIf="items().length; else empty">
    <div class="notif-row" *ngFor="let n of items()" [class.unread]="n.status === 'Unread'">
      <div class="notif-main">
        <span class="tag tag-slate">{{ n.notification_type }}</span>
        <strong>{{ n.title }}</strong>
        <p>{{ n.message }}</p>
        <span class="muted" style="font-size:12px">{{ n.created_at | date:'medium' }}</span>
      </div>
      <button class="btn-ghost btn-sm" *ngIf="n.status === 'Unread'" (click)="markRead(n)">Mark read</button>
    </div>
  </div>
  <ng-template #empty>
    <div class="panel empty-state">
      <strong>No notifications</strong>
      You're caught up — nothing needs your attention right now.
    </div>
  </ng-template>
  `,
  styles: [`
    .page-head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; }
    .notif-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 14px; padding: 16px 20px; border-bottom: 1px solid var(--line); }
    .notif-row:last-child { border-bottom: none; }
    .notif-row.unread { background: #FAFAF7; border-left: 3px solid var(--seal); }
    .notif-main strong { display: block; margin: 6px 0 3px; font-family: var(--font-body); font-size: 14.5px; font-weight: 600; }
    .notif-main p { margin: 0 0 6px; font-size: 13.5px; color: var(--ink-soft); }
  `],
})
export class NotificationsComponent implements OnInit {
  private svc = inject(NotificationsService);
  items = signal<AppNotification[]>([]);
  error = signal('');

  unread() { return this.items().filter(n => n.status === 'Unread'); }

  ngOnInit() {
    this.svc.list().subscribe({
      next: list => this.items.set(list),
      error: () => this.error.set('Unable to load notifications.'),
    });
  }

  markRead(n: AppNotification) {
    this.svc.markRead(n.id).subscribe(updated => {
      this.items.set(this.items().map(x => x.id === updated.id ? updated : x));
    });
  }

  markAll() {
    this.svc.markAllRead().subscribe(() => {
      this.items.set(this.items().map(x => ({ ...x, status: 'Read' as const })));
    });
  }
}
