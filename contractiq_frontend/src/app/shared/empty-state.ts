import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="empty-state">
      <div class="icon">📭</div>
      <h3>{{ title }}</h3>
      <p>{{ message }}</p>
    </div>
  `,
  styles: [`
    .empty-state {
      padding: 40px 20px;
      text-align: center;
      color: #666;
    }

    .icon {
      font-size: 36px;
      margin-bottom: 10px;
    }

    h3 {
      margin: 0 0 6px;
      color: #444;
    }

    p {
      margin: 0;
    }
  `]
})
export class EmptyState {
  @Input() title = 'No data found';
  @Input() message = 'There is nothing to display.';
}
