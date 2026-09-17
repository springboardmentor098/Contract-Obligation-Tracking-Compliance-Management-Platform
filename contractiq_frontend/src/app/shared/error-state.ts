import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-error-state',
  standalone: true,
  imports: [CommonModule, MatButtonModule],
  template: `
    <div class="error-state">
      <div class="icon">⚠️</div>
      <h3>{{ title }}</h3>
      <p>{{ message }}</p>

      <button
        mat-raised-button
        color="primary"
        *ngIf="showRetry"
        (click)="retry.emit()">
        Retry
      </button>
    </div>
  `,
  styles: [`
    .error-state {
      padding: 40px 20px;
      text-align: center;
      color: #c62828;
    }

    .icon {
      font-size: 36px;
      margin-bottom: 10px;
    }

    h3 {
      margin: 0 0 6px;
    }

    p {
      margin: 0 0 16px;
      color: #666;
    }
  `]
})
export class ErrorState {
  @Input() title = 'Something went wrong';
  @Input() message = 'Unable to load the requested data.';
  @Input() showRetry = true;

  @Output() retry = new EventEmitter<void>();
}
