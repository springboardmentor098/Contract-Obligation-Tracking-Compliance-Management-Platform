import {
  Component,
  inject,
  OnInit
} from '@angular/core';

import {
  RouterLink,
  RouterLinkActive,
  RouterOutlet
} from '@angular/router';

import { AuthService } from '../core/services/auth.service';
import { UserService } from '../core/services/user.service';
import { User } from '../core/models/models';

@Component({
  selector: 'cq-layout',
  standalone: true,

  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive
  ],

  templateUrl: './layout.component.html',
  styleUrl: './layout.component.css'
})
export class LayoutComponent implements OnInit {

  // ============================================================
  // SERVICES
  // ============================================================

  readonly auth = inject(AuthService);

  private readonly userService =
    inject(UserService);


  // ============================================================
  // SIDEBAR
  // ============================================================

  sidebarOpen = true;


  // ============================================================
  // CURRENT USER
  // ============================================================

  currentUser: User | null = null;


  // ============================================================
  // NAVIGATION
  // ============================================================

  nav = [

    {
      label: 'Dashboard',
      icon: 'dashboard',
      route: '/dashboard'
    },

    {
      label: 'Contracts',
      icon: 'description',
      route: '/contracts'
    },

    {
      label: 'Obligations',
      icon: 'task_alt',
      route: '/obligations'
    },

    {
      label: 'Renewals',
      icon: 'event_repeat',
      route: '/renewals'
    },

    {
      label: 'Compliance',
      icon: 'verified_user',
      route: '/compliance'
    },

    {
      label: 'Reports & Analytics',
      icon: 'bar_chart',
      route: '/reports'
    },

    {
      label: 'Audit / Activity',
      icon: 'history',
      route: '/audit'
    },

    {
      label: 'User Management',
      icon: 'manage_accounts',
      route: '/users'
    }

  ];


  // ============================================================
  // INITIALIZATION
  // ============================================================

  ngOnInit(): void {

    this.loadUserProfile();

  }


  // ============================================================
  // USER AVATAR INITIAL
  // ============================================================

  getUserInitial(): string {

    if (
      this.currentUser &&
      this.currentUser.full_name
    ) {

      return this.currentUser.full_name
        .charAt(0)
        .toUpperCase();

    }

    return '?';

  }


  // ============================================================
  // LOAD ACTUAL USER PROFILE
  // ============================================================

  private loadUserProfile(): void {

    const token = this.auth.token();


    if (!token) {

      console.error(
        'No authentication token found.'
      );

      return;

    }


    try {

      // --------------------------------------------------------
      // Decode JWT
      // --------------------------------------------------------

      const parts = token.split('.');


      if (parts.length !== 3) {

        console.error(
          'Invalid JWT token.'
        );

        return;

      }


      const base64Payload = parts[1]
        .replace(/-/g, '+')
        .replace(/_/g, '/');


      const paddedPayload =
        base64Payload +
        '='.repeat(
          (4 - base64Payload.length % 4) % 4
        );


      const payload = JSON.parse(
        atob(paddedPayload)
      );


      // --------------------------------------------------------
      // Get user ID
      // --------------------------------------------------------

      const userId = Number(
        payload.sub
      );


      if (!userId) {

        console.error(
          'User ID was not found in JWT.'
        );

        return;

      }


      // --------------------------------------------------------
      // Get actual user from backend
      // --------------------------------------------------------

      this.userService
        .get(userId)
        .subscribe({

          next: (user: User) => {

            console.log(
              'Logged-in user profile:',
              user
            );


            // Save actual user in component
            this.currentUser = user;


            // Save actual user in localStorage
            this.auth.setCurrentUser(
              user
            );

          },


          error: (error) => {

            console.error(
              'Unable to load user profile:',
              error
            );

          }

        });


    } catch (error) {

      console.error(
        'Unable to decode JWT:',
        error
      );

    }

  }


  // ============================================================
  // TOGGLE SIDEBAR
  // ============================================================

  toggleSidebar(): void {

    this.sidebarOpen =
      !this.sidebarOpen;

  }

}
