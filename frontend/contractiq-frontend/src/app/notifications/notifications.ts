import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

import {
  NotificationService,
  Notification
} from '../services/notification';


@Component({
  selector: 'app-notifications',
  standalone: true,

  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule
  ],

  templateUrl: './notifications.html',
  styleUrl: './notifications.less'
})


export class Notifications implements OnInit {

  // =========================
  // DATA
  // =========================

  notifications: Notification[] = [];


  // =========================
  // UI STATES
  // =========================

  loading = true;

  errorMessage = '';

  isEmpty = false;

  markingAsRead = false;

  markingAllAsRead = false;


  // =========================
  // CONSTRUCTOR
  // =========================

  constructor(
    private notificationService: NotificationService,
    private cdr: ChangeDetectorRef
  ) {}


  // =========================
  // INIT
  // =========================

  ngOnInit(): void {

    this.loadNotifications();

  }


  // =========================
  // LOAD NOTIFICATIONS
  // =========================

  loadNotifications(): void {

    this.loading = true;

    this.errorMessage = '';

    this.isEmpty = false;

    this.cdr.markForCheck();


    this.notificationService
      .getNotifications()
      .subscribe({

        // =========================
        // SUCCESS
        // =========================

        next: (data: Notification[]) => {

          console.log(
            'Notifications:',
            data
          );


          this.notifications = data || [];


          // IMPORTANT
          // API response aa gaya,
          // ab loading hatao.

          this.loading = false;


          // Empty check

          this.isEmpty =
            this.notifications.length === 0;


          // Force Angular UI update

          this.cdr.markForCheck();

        },


        // =========================
        // ERROR
        // =========================

        error: (error: any) => {

          console.error(
            'Notifications error:',
            error
          );


          this.loading = false;


          if (error.status === 401) {

            this.errorMessage =
              'Your session has expired. Please login again.';

          }

          else if (error.status === 403) {

            this.errorMessage =
              'You are not authorized to view notifications.';

          }

          else if (error.status === 0) {

            this.errorMessage =
              'Unable to connect to the backend server.';

          }

          else {

            this.errorMessage =
              'Failed to load notifications. Please try again.';

          }


          // Force UI update

          this.cdr.markForCheck();

        }

      });

  }


  // =========================
  // MARK ONE AS READ
  // =========================

  markAsRead(
    notification: Notification
  ): void {

    // Already read

    if (notification.status === 'Read') {

      return;

    }


    this.markingAsRead = true;

    this.cdr.markForCheck();


    this.notificationService
      .markAsRead(notification.id)
      .subscribe({

        next: (
          updatedNotification: Notification
        ) => {

          const index =
            this.notifications.findIndex(
              item =>
                item.id === notification.id
            );


          if (index !== -1) {

            this.notifications[index] =
              updatedNotification;

          }


          this.markingAsRead = false;

          this.cdr.markForCheck();

        },


        error: (error: any) => {

          console.error(
            'Mark notification as read error:',
            error
          );


          this.markingAsRead = false;

          this.cdr.markForCheck();

        }

      });

  }


  // =========================
  // MARK ALL AS READ
  // =========================

  markAllAsRead(): void {

    const unreadCount =
      this.notifications.filter(
        notification =>
          notification.status === 'Unread'
      ).length;


    // Nothing to update

    if (unreadCount === 0) {

      return;

    }


    this.markingAllAsRead = true;

    this.cdr.markForCheck();


    this.notificationService
      .markAllAsRead()
      .subscribe({

        next: () => {

          this.notifications =
            this.notifications.map(
              notification => ({

                ...notification,

                status: 'Read',

                read_at:
                  new Date().toISOString()

              })
            );


          this.markingAllAsRead = false;

          this.cdr.markForCheck();

        },


        error: (error: any) => {

          console.error(
            'Mark all notifications as read error:',
            error
          );


          this.markingAllAsRead = false;

          this.cdr.markForCheck();

        }

      });

  }


  // =========================
  // UNREAD COUNT
  // =========================

  getUnreadCount(): number {

    return this.notifications.filter(
      notification =>
        notification.status === 'Unread'
    ).length;

  }


  // =========================
  // NOTIFICATION ICON
  // =========================

  getNotificationIcon(
    type: string
  ): string {

    switch (type) {

      case 'Obligation Due Alert':

        return 'event';


      case 'Compliance Alert':

        return 'warning';


      case 'Renewal Alert':

        return 'autorenew';


      default:

        return 'notifications';

    }

  }


  // =========================
  // NOTIFICATION CLASS
  // =========================

  getNotificationClass(
    type: string
  ): string {

    switch (type) {

      case 'Obligation Due Alert':

        return 'obligation';


      case 'Compliance Alert':

        return 'compliance';


      case 'Renewal Alert':

        return 'renewal';


      default:

        return 'default';

    }

  }


  // =========================
  // STATUS CLASS
  // =========================

  getStatusClass(
    status: string
  ): string {

    switch (status) {

      case 'Unread':

        return 'unread';


      case 'Read':

        return 'read';


      default:

        return 'default';

    }

  }


  // =========================
  // RETRY
  // =========================

  retry(): void {

    this.loadNotifications();

  }

}