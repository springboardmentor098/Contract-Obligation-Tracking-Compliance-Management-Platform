import { CommonModule } from '@angular/common';
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { NotificationService } from '../services/notification.service';
import { Notification } from '../models/notification.model';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './notifications.html',
  styleUrls: ['./notifications.css']
})
export class Notifications implements OnInit {

  notifications: Notification[] = [];

  loading = false;
  actionLoading = false;

  errorMessage = '';
  successMessage = '';

  constructor(
    private readonly notificationService: NotificationService,
    private readonly router: Router,
    private readonly cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    console.log('Notifications: loading started');

    this.notificationService.getNotifications().subscribe({
      next: (data: Notification[]) => {
        console.log('Notifications: received', data);

        this.notifications = Array.isArray(data)
          ? data
          : [];

        this.loading = false;

        this.cdr.detectChanges();

        console.log(
          'Notifications: loading =',
          this.loading
        );
      },

      error: (error: HttpErrorResponse) => {
        console.error(
          'Notifications: API error',
          error
        );

        this.notifications = [];
        this.loading = false;

        if (error.status === 401) {
          this.errorMessage =
            'Your session has expired. Please log in again.';
        } else if (error.status === 403) {
          this.errorMessage =
            'You are not authorized to view notifications.';
        } else {
          this.errorMessage =
            error.error?.detail ??
            'Failed to load notifications.';
        }

        this.cdr.detectChanges();
      },

      complete: () => {
        console.log(
          'Notifications: request completed'
        );

        this.loading = false;

        this.cdr.detectChanges();
      }
    });
  }

  isRead(notification: Notification): boolean {
    return String(
      notification.status ?? ''
    ).toLowerCase() === 'read';
  }

  getUnreadCount(): number {
    return this.notifications.filter(
      notification =>
        !this.isRead(notification)
    ).length;
  }

  getReadCount(): number {
    return this.notifications.filter(
      notification =>
        this.isRead(notification)
    ).length;
  }

  openNotification(notification: Notification): void {

    const notificationType =
      String(
        notification.notification_type ?? ''
      ).toLowerCase();

    const contractId =
      notification.contract_id;

    const obligationId =
      notification.obligation_id;

    // Mark as read when opened.
    if (!this.isRead(notification)) {

      this.notificationService
        .markAsRead(notification.id)
        .subscribe({
          next: (result) => {
            notification.status = result.status;
            notification.read_at = result.read_at;

            this.actionLoading = false;
            this.cdr.detectChanges();
          },

          error: (error: HttpErrorResponse) => {
            console.error(
              'Open notification - mark as read error:',
              error
            );

            this.actionLoading = false;
            this.cdr.detectChanges();
          }
        });
    }

    // Compliance notification -> Compliance details
    if (
      notificationType.includes('compliance') &&
      contractId !== null &&
      contractId !== undefined
    ) {
      this.router.navigate(
        ['/compliance'],
        {
          queryParams: {
            contractId: contractId
          }
        }
      );

      return;
    }

    // Obligation notification -> Obligations
    if (
      notificationType.includes('obligation')
    ) {
      if (
        obligationId !== null &&
        obligationId !== undefined
      ) {
        this.router.navigate(
          ['/obligations'],
          {
            queryParams: {
              obligationId: obligationId
            }
          }
        );
      } else if (
        contractId !== null &&
        contractId !== undefined
      ) {
        this.router.navigate(
          ['/obligations'],
          {
            queryParams: {
              contractId: contractId
            }
          }
        );
      } else {
        this.router.navigate(
          ['/obligations']
        );
      }

      return;
    }

    // Renewal notification -> Renewals
    if (
      notificationType.includes('renewal')
    ) {
      if (
        contractId !== null &&
        contractId !== undefined
      ) {
        this.router.navigate(
          ['/renewals'],
          {
            queryParams: {
              contractId: contractId
            }
          }
        );
      } else {
        this.router.navigate(
          ['/renewals']
        );
      }

      return;
    }

    // Contract / approval notification -> Contracts
    if (
      notificationType.includes('approval') ||
      notificationType.includes('contract')
    ) {
      if (
        contractId !== null &&
        contractId !== undefined
      ) {
        this.router.navigate(
          ['/contracts'],
          {
            queryParams: {
              contractId: contractId
            }
          }
        );
      } else {
        this.router.navigate(
          ['/contracts']
        );
      }

      return;
    }

    // Unknown notification type
    this.router.navigate(
      ['/notifications']
    );
  }

  markAsRead(notification: Notification): void {

    if (this.isRead(notification)) {
      return;
    }

    this.actionLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.notificationService
      .markAsRead(notification.id)
      .subscribe({
        next: (result) => {

          notification.status = result.status;
          notification.read_at = result.read_at;

          this.actionLoading = false;

          this.successMessage =
            'Notification marked as read.';

          this.cdr.detectChanges();
        },

        error: (error: HttpErrorResponse) => {

          console.error(
            'Mark as read error:',
            error
          );

          this.actionLoading = false;

          this.errorMessage =
            error.error?.detail ??
            'Failed to mark notification as read.';

          this.cdr.detectChanges();
        }
      });
  }

  markAllAsRead(): void {

    const unreadCount =
      this.getUnreadCount();

    if (unreadCount === 0) {
      return;
    }

    this.actionLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.notificationService
      .markAllAsRead()
      .subscribe({
        next: (result) => {

          const now =
            new Date().toISOString();

          this.notifications =
            this.notifications.map(
              (notification: Notification) => ({
                ...notification,
                status: 'Read',
                read_at: now
              })
            );

          this.actionLoading = false;

          this.successMessage =
            result.message ??
            'All notifications marked as read.';

          this.cdr.detectChanges();
        },

        error: (error: HttpErrorResponse) => {

          console.error(
            'Mark all as read error:',
            error
          );

          this.actionLoading = false;

          this.errorMessage =
            error.error?.detail ??
            'Failed to mark all notifications as read.';

          this.cdr.detectChanges();
        }
      });
  }
}