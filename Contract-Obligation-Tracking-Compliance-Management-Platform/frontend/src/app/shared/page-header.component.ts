import { Component, Input } from '@angular/core';

@Component({
  selector: 'cq-page-header',
  standalone: true,
  template: `
    <div class="page-head">
      <div>
        <div class="eyebrow">{{ eyebrow }}</div>
        <h1>{{ title }}</h1>
        <p>{{ subtitle }}</p>
      </div>
      <div class="actions"><ng-content /></div>
    </div>
  `,
  styles: [`
    .page-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:22px}.eyebrow{font-size:10px;font-weight:800;letter-spacing:.12em;color:#2f7ef5;text-transform:uppercase;margin-bottom:5px}h1{margin:0;font-size:25px;letter-spacing:-.03em;color:#13213a}p{margin:6px 0 0;color:#778398;font-size:12px}.actions{display:flex;gap:8px}@media(max-width:700px){.page-head{align-items:flex-start;flex-direction:column}.actions{width:100%}}
  `]
})
export class PageHeaderComponent {
  @Input() title = '';
  @Input() subtitle = '';
  @Input() eyebrow = 'ContractIQ';
}
