import { Component, Input } from '@angular/core';

@Component({
  selector: 'cq-status',
  standalone: true,
  template: `<span class="status" [class]="tone">{{ label }}</span>`,
  styles: [`
    .status{display:inline-flex;align-items:center;padding:4px 9px;border-radius:999px;font-size:10px;font-weight:800;white-space:nowrap}.success{background:#e9f8f0;color:#158152}.warning{background:#fff6df;color:#a36b00}.danger{background:#ffebeb;color:#b63232}.info{background:#e8f2ff;color:#2269bf}.neutral{background:#eef1f5;color:#637084}
  `]
})
export class StatusComponent {
  @Input() label = '';
  get tone(): string {
    const s = this.label.toLowerCase();
    if (s.includes('active') || s.includes('completed') || s.includes('renewed') || s.includes('compliant') || s.includes('approved')) return 'success';
    if (s.includes('pending') || s.includes('review') || s.includes('upcoming') || s.includes('progress') || s.includes('delayed')) return 'warning';
    if (s.includes('overdue') || s.includes('expired') || s.includes('non-compliant') || s.includes('risk') || s.includes('terminated')) return 'danger';
    if (s.includes('draft') || s.includes('cancel')) return 'neutral';
    return 'info';
  }
}
