import { Component, ChangeDetectorRef, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api } from '../../services/api';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications.html',
  styleUrl: './notifications.scss',
})
export class Notifications implements OnInit {
  private api = inject(Api);
  private cdr = inject(ChangeDetectorRef);

  notifications: any[] = [];
  loading = false;
  error = '';
  actionLoading = false;

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {
    console.log('NOTIFICATIONS: LOAD START');

    this.loading = true;
    this.error = '';

    this.api.getNotifications().subscribe({
      next: (data) => {
        console.log('NOTIFICATIONS: API SUCCESS', data);

        this.notifications = Array.isArray(data) ? data : [];
        this.loading = false;

        console.log('NOTIFICATIONS: FINAL STATE', {
          loading: this.loading,
          count: this.notifications.length,
          unread: this.unreadCount
        });

        this.cdr.detectChanges();
      },

      error: (err) => {
        console.error('NOTIFICATIONS: API ERROR', err);

        this.loading = false;

        if (err?.status === 401) {
          this.error = 'Your session has expired. Please sign in again.';
        } else if (err?.status === 403) {
          this.error = 'You do not have permission to view notifications.';
        } else {
          this.error =
            'Unable to load notifications. Please check the backend connection and try again.';
        }

        this.cdr.detectChanges();
      },
    });
  }

  markAsRead(notification: any): void {
    if (!notification?.id || notification.status === 'Read') {
      return;
    }

    this.api.markNotificationRead(notification.id).subscribe({
      next: () => {
        notification.status = 'Read';
        notification.read_at = new Date().toISOString();
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('NOTIFICATIONS: MARK READ ERROR', err);
      },
    });
  }

  markAllAsRead(): void {
    const unread = this.unreadCount;

    if (unread === 0 || this.actionLoading) {
      return;
    }

    this.actionLoading = true;

    this.api.markAllNotificationsRead().subscribe({
      next: () => {
        const now = new Date().toISOString();

        this.notifications = this.notifications.map((notification) => ({
          ...notification,
          status: 'Read',
          read_at: notification.read_at ?? now,
        }));

        this.actionLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('NOTIFICATIONS: MARK ALL READ ERROR', err);
        this.actionLoading = false;
        this.cdr.detectChanges();
      },
    });
  }

  get unreadCount(): number {
    return this.notifications.filter(
      (notification) => notification.status === 'Unread'
    ).length;
  }

  get notificationCount(): number {
    return this.notifications.length;
  }

  getTypeClass(type: string): string {
    const value = (type || '').toLowerCase();

    if (value.includes('overdue')) {
      return 'overdue';
    }

    if (value.includes('compliance')) {
      return 'compliance';
    }

    if (value.includes('renewal')) {
      return 'renewal';
    }

    if (value.includes('approval')) {
      return 'approval';
    }

    if (value.includes('status')) {
      return 'status';
    }

    return 'default';
  }

  formatDate(value: string | null | undefined): string {
    if (!value) {
      return '';
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return '';
    }

    return date.toLocaleString();
  }
}
