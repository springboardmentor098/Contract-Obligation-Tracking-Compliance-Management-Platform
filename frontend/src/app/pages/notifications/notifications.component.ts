import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
  Notification,
  NotificationService
} from '../../services/notification.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  templateUrl: './notifications.component.html',
  styleUrl: './notifications.component.scss'
})
export class NotificationsComponent implements OnInit {

  private readonly notificationService =
    inject(NotificationService);

  notifications: Notification[] = [];
  filteredNotifications: Notification[] = [];

  loading = true;
  error = '';

  showUnreadOnly = false;

  unreadCount = 0;

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.loading = true;
    this.error = '';

    this.notificationService
      .getNotifications()
      .subscribe({
        next: (notifications) => {
          this.notifications = notifications;
          this.updateUnreadCount();
          this.applyFilter();
          this.loading = false;
        },

        error: (error) => {
          console.error(
            'Notifications API error:',
            error
          );

          this.loading = false;

          this.error =
            this.getErrorMessage(
              error,
              'Unable to load notifications.'
            );
        }
      });
  }

  toggleUnreadFilter(): void {
    this.showUnreadOnly =
      !this.showUnreadOnly;

    this.applyFilter();
  }

  applyFilter(): void {
    if (this.showUnreadOnly) {
      this.filteredNotifications =
        this.notifications.filter(
          (notification) =>
            !notification.read_at
        );
    } else {
      this.filteredNotifications = [
        ...this.notifications
      ];
    }
  }

  markAsRead(
    notification: Notification
  ): void {

    if (notification.read_at) {
      return;
    }

    this.notificationService
      .markAsRead(notification.id)
      .subscribe({
        next: (updatedNotification) => {

          this.replaceNotification(
            updatedNotification
          );

          this.updateUnreadCount();
          this.applyFilter();
        },

        error: (error) => {
          console.error(
            'Mark notification as read error:',
            error
          );

          this.error =
            this.getErrorMessage(
              error,
              'Unable to mark notification as read.'
            );
        }
      });
  }

  markAsUnread(
    notification: Notification
  ): void {

    this.notificationService
      .markAsUnread(notification.id)
      .subscribe({
        next: (updatedNotification) => {

          this.replaceNotification(
            updatedNotification
          );

          this.updateUnreadCount();
          this.applyFilter();
        },

        error: (error) => {
          console.error(
            'Mark notification as unread error:',
            error
          );

          this.error =
            this.getErrorMessage(
              error,
              'Unable to mark notification as unread.'
            );
        }
      });
  }

  markAllAsRead(): void {

    if (this.unreadCount === 0) {
      return;
    }

    this.notificationService
      .markAllAsRead()
      .subscribe({
        next: () => {
          this.notifications =
            this.notifications.map(
              (notification) => ({
                ...notification,
                read_at:
                  notification.read_at ||
                  new Date().toISOString()
              })
            );

          this.updateUnreadCount();
          this.applyFilter();
        },

        error: (error) => {
          console.error(
            'Mark all notifications as read error:',
            error
          );

          this.error =
            this.getErrorMessage(
              error,
              'Unable to mark all notifications as read.'
            );
        }
      });
  }

  deleteNotification(
    notification: Notification
  ): void {

    const confirmed =
      window.confirm(
        `Delete notification "${notification.title}"?`
      );

    if (!confirmed) {
      return;
    }

    this.notificationService
      .deleteNotification(notification.id)
      .subscribe({
        next: () => {

          this.notifications =
            this.notifications.filter(
              (item) =>
                item.id !== notification.id
            );

          this.updateUnreadCount();
          this.applyFilter();
        },

        error: (error) => {
          console.error(
            'Delete notification error:',
            error
          );

          this.error =
            this.getErrorMessage(
              error,
              'Unable to delete notification.'
            );
        }
      });
  }

  refresh(): void {
    this.loadNotifications();
  }

  isUnread(
    notification: Notification
  ): boolean {
    return !notification.read_at;
  }

  getNotificationIcon(
    type: string
  ): string {

    const normalizedType =
      type
        ?.toLowerCase()
        .replace(/[\s_-]+/g, '');

    switch (normalizedType) {

      case 'renewal':
      case 'renewalreminder':
        return 'event_repeat';

      case 'obligation':
      case 'obligationreminder':
        return 'assignment';

      case 'compliance':
        return 'verified_user';

      case 'contract':
        return 'description';

      case 'warning':
      case 'alert':
        return 'warning';

      case 'success':
        return 'check_circle';

      case 'error':
        return 'error';

      default:
        return 'notifications';
    }
  }

  getNotificationClass(
    notification: Notification
  ): string {

    if (this.isUnread(notification)) {
      return 'unread';
    }

    return 'read';
  }

  formatDate(
    date: string | null
  ): string {

    if (!date) {
      return '—';
    }

    return new Date(date).toLocaleString();
  }

  private replaceNotification(
    updatedNotification: Notification
  ): void {

    this.notifications =
      this.notifications.map(
        (notification) =>
          notification.id ===
          updatedNotification.id
            ? updatedNotification
            : notification
      );
  }

  private updateUnreadCount(): void {

    this.unreadCount =
      this.notifications.filter(
        (notification) =>
          !notification.read_at
      ).length;
  }

  private getErrorMessage(
    error: any,
    fallback: string
  ): string {

    if (error?.status === 401) {
      return 'Your session has expired. Please log in again.';
    }

    if (error?.status === 403) {
      return 'You do not have permission to access notifications.';
    }

    if (error?.status === 404) {
      return 'Notification was not found.';
    }

    if (error?.status === 0) {
      return 'Unable to connect to the backend. Please make sure FastAPI is running.';
    }

    return (
      error?.error?.detail ||
      fallback
    );
  }
}