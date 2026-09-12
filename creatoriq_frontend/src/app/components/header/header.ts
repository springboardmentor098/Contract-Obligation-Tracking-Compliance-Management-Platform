import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Auth, CurrentUser } from '../../services/auth';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [],
  templateUrl: './header.html',
  styleUrl: './header.css'
})
export class Header implements OnInit {

  currentUser: CurrentUser | null = null;

  constructor(
    private auth: Auth,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadCurrentUser();
  }

  private loadCurrentUser(): void {
    if (!this.auth.isLoggedIn()) {
      return;
    }

    this.auth.getCurrentUser().subscribe({
      next: (user) => {
        this.currentUser = user;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Unable to load current user:', error);

        // Use JWT role as a fallback if the user details request fails.
        const role = this.auth.getRole();

        this.currentUser = {
          id: this.auth.getUserId() ?? 0,
          full_name: 'User',
          email: '',
          role: role ?? 'User',
          is_active: true
        };

        this.cdr.detectChanges();
      }
    });
  }

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }

  get userInitial(): string {
    if (!this.currentUser?.full_name) {
      return 'U';
    }

    return this.currentUser.full_name.charAt(0).toUpperCase();
  }
}