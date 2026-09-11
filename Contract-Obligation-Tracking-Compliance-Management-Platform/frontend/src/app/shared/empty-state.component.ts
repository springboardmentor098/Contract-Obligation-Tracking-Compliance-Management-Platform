import { Component, Input } from '@angular/core';

@Component({
  selector: 'cq-empty',
  standalone: true,
  template: `<div class="empty"><span class="material-icons-round">{{icon}}</span><b>{{title}}</b><p>{{message}}</p></div>`,
  styles: [`.empty{padding:42px 20px;text-align:center;color:#7e8a9d}.empty .material-icons-round{font-size:35px;color:#b6c0cf}.empty b{display:block;color:#3b485b;font-size:13px;margin-top:8px}.empty p{font-size:11px;margin:5px 0}`]
})
export class EmptyStateComponent {
  @Input() title = 'Nothing to display';
  @Input() message = 'No records were returned by the backend.';
  @Input() icon = 'inbox';
}
