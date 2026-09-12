import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import {
  Notifications as NotificationsService,
  Notification
} from '../../services/notifications';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [],
  templateUrl: './notifications.html',
  styleUrl: './notifications.css'
})
export class Notifications implements OnInit {

  notifications: Notification[] = [];

  loading = false;
  errorMessage = '';

  constructor(
    private notificationsService: NotificationsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.loading = true;
    this.errorMessage = '';

    this.cdr.detectChanges();

    this.notificationsService.getNotifications().subscribe({
      next: (data) => {
        console.log('Notifications data received:', data);
        console.log('Notifications count:', data.length);

        this.notifications = data;
        this.loading = false;

        this.cdr.detectChanges();
      },

      error: (error) => {
        console.error('Notifications API error:', error);

        this.loading = false;

        if (error.status === 401) {
          this.errorMessage = 'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.errorMessage = 'You do not have permission to view notifications.';
        } else {
          this.errorMessage = 'Unable to load notifications.';
        }

        this.cdr.detectChanges();
      }
    });
  }
}