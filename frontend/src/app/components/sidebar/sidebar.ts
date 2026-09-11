import { Component } from '@angular/core';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    MatListModule,
    MatIconModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class Sidebar {}
