import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import {
  Notification,
  NotificationService
} from '../../core/services/notification.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications.html',
  styleUrl: './notifications.scss'
})
export class Notifications implements OnInit {
  private readonly notificationService = inject(NotificationService);
  private readonly cdr = inject(ChangeDetectorRef);

  notifications: Notification[] = [];
  loading = true;
  error = '';

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.loading = true;
    this.error = '';

    this.notificationService.getNotifications().subscribe({
      next: (response: any) => {
        console.log('Notifications API response:', response);

        // Backend currently returns:
        // { value: [...], Count: 1 }
        //
        // This also supports a direct array response.
        if (Array.isArray(response)) {
          this.notifications = response;
        } else if (Array.isArray(response?.value)) {
          this.notifications = response.value;
        } else {
          this.notifications = [];
        }

        this.loading = false;
        this.cdr.detectChanges();
      },

      error: (err) => {
        console.error('Notification loading error:', err);

        this.error = 'Unable to load notifications.';
        this.loading = false;

        this.cdr.detectChanges();
      }
    });
  }

  get unreadCount(): number {
    return this.notifications.filter(
      notification => !notification.is_read
    ).length;
  }

  get readCount(): number {
    return this.notifications.filter(
      notification => notification.is_read
    ).length;
  }

  getNotificationClass(type: string): string {
    return (type || 'general')
      .toLowerCase()
      .replace(/\s+/g, '-');
  }
}