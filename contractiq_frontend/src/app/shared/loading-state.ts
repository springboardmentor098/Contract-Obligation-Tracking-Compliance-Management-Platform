import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-loading-state',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule],
  template: `
    <div class="loading-state">
      <mat-spinner [diameter]="diameter"></mat-spinner>
      <p>{{ message }}</p>
    </div>
  `,
  styles: [`
    .loading-state {
      min-height: 180px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;
      text-align: center;
    }

    p {
      margin: 0;
      color: #666;
    }
  `]
})
export class LoadingState {
  @Input() message = 'Loading...';
  @Input() diameter = 40;
}
