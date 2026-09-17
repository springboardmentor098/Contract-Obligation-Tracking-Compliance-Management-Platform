import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import {
  NotificationsService,
  Notification
} from '../services/notifications';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatTableModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule
  ],
  templateUrl: './notifications.html',
  styleUrl: './notifications.css'
})
export class Notifications implements OnInit {

  notifications: Notification[] = [];
  filteredNotifications: Notification[] = [];

  loading = false;
  errorMessage = '';
  successMessage = '';

  searchText = '';
  selectedStatus = '';

  selectedNotification: Notification | null = null;

  displayedColumns = [
    'title',
    'notification_type',
    'message',
    'status',
    'created_at',
    'actions'
  ];

  statuses = [
    'Unread',
    'Read'
  ];

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

    this.notificationsService.getNotifications().subscribe({
      next: (data) => {
        this.notifications = data;
        this.applyFilters();
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Notifications API error:', error);
        this.errorMessage =
          error.error?.detail || 'Unable to load notifications.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  applyFilters(): void {
    const search = this.searchText.toLowerCase().trim();

    this.filteredNotifications = this.notifications.filter(notification => {

      const matchesSearch =
        !search ||
        notification.title.toLowerCase().includes(search) ||
        notification.message.toLowerCase().includes(search) ||
        notification.notification_type.toLowerCase().includes(search);

      const matchesStatus =
        !this.selectedStatus ||
        notification.status === this.selectedStatus;

      return matchesSearch && matchesStatus;
    });
  }

  clearFilters(): void {
    this.searchText = '';
    this.selectedStatus = '';
    this.applyFilters();
  }

  getUnreadCount(): number {
    return this.notifications.filter(
      notification => notification.status === 'Unread'
    ).length;
  }

  getReadCount(): number {
    return this.notifications.filter(
      notification => notification.status === 'Read'
    ).length;
  }

  markAsRead(notification: Notification): void {
    if (notification.status === 'Read') {
      return;
    }

    this.notificationsService.markAsRead(notification.id).subscribe({
      next: (updatedNotification) => {
        const index = this.notifications.findIndex(
          item => item.id === updatedNotification.id
        );

        if (index !== -1) {
          this.notifications[index] = updatedNotification;
        }

        this.applyFilters();

        this.successMessage = 'Notification marked as read.';
        this.errorMessage = '';

        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Mark notification as read error:', error);
        this.errorMessage =
          error.error?.detail || 'Unable to mark notification as read.';
        this.cdr.markForCheck();
      }
    });
  }

  markAllAsRead(): void {
    if (this.getUnreadCount() === 0) {
      return;
    }

    this.notificationsService.markAllAsRead().subscribe({
      next: () => {
        this.notifications = this.notifications.map(notification => ({
          ...notification,
          status: 'Read',
          read_at: notification.read_at || new Date().toISOString()
        }));

        this.applyFilters();

        this.successMessage =
          'All notifications marked as read.';
        this.errorMessage = '';

        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Mark all notifications as read error:', error);
        this.errorMessage =
          error.error?.detail ||
          'Unable to mark all notifications as read.';
        this.cdr.markForCheck();
      }
    });
  }

  viewNotification(notification: Notification): void {
    this.loading = true;
    this.errorMessage = '';

    this.notificationsService.getNotification(notification.id).subscribe({
      next: (data) => {
        this.selectedNotification = data;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Notification details error:', error);
        this.errorMessage =
          error.error?.detail ||
          'Unable to load notification details.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  closeDetails(): void {
    this.selectedNotification = null;
  }

  getStatusClass(status: string): string {
    return status.toLowerCase().replace(/\s+/g, '-');
  }
}
