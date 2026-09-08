import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-login',
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {

  email = '';
  password = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  login() {

    this.authService.login(
      this.email,
      this.password
    ).subscribe({

      next: (response: any) => {

        console.log('Login Success:', response);

        this.authService.saveToken(
          response.access_token
        );

        this.router.navigate(['/dashboard']);
      },

      error: (error: any) => {

        console.error('Login Failed:', error);

        alert('Invalid email or password');

      }

    });

  }

}