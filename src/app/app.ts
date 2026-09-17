import {
  Component,
  inject
} from '@angular/core';

import {
  Router,
  RouterLink,
  RouterOutlet,
  NavigationEnd
} from '@angular/router';

import { filter } from 'rxjs';

import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',

  standalone: true,

  imports: [
    RouterLink,
    RouterOutlet
  ],

  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {

  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  constructor() {

    this.router.events

      .pipe(
        filter(
          event =>
            event instanceof NavigationEnd
        )
      )

      .subscribe((event) => {

        console.log(
          'Angular navigation completed:',
          (event as NavigationEnd).urlAfterRedirects
        );

        console.log(
          'Authentication token exists:',
          this.authService.isLoggedIn()
        );

      });
  }

  get isLoggedIn(): boolean {

    return this.authService.isLoggedIn();
  }

  logout(): void {

    console.log(
      'Logging out...'
    );

    this.authService.logout();

    this.router.navigateByUrl('/login');
  }
}