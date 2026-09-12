import { Component } from '@angular/core';
import { Router, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { Auth } from '../services/auth';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './layout.html',
  styleUrl: './layout.less'
})
export class Layout {

  userName = 'User';
  userRole = 'Employee';

  constructor(
    private auth: Auth,
    private router: Router
  ) {
    const role = localStorage.getItem('role');

    if (role) {
      this.userRole = role;
    }
  }

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
