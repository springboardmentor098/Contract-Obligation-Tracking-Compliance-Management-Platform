import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../services/auth';
import { UserService, UserProfile } from '../services/user';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit {

  profile: UserProfile | null = null;
  loading = true;
  errorMessage = '';

  constructor(
    private authService: AuthService,
    private userService: UserService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    const userId = this.authService.getUserId();

    if (!userId) {
      this.errorMessage = 'Unable to identify the logged-in user.';
      this.loading = false;
      this.cdr.detectChanges();
      return;
    }

    this.userService.getUser(Number(userId)).subscribe({
      next: (user) => {
        this.profile = user;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Unable to load your profile.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }
}
