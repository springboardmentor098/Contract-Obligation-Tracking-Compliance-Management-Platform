import { Component, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { AuditService } from '../../core/services/audit.service';
import { Activity } from '../../core/models/models';
import { PageHeaderComponent } from '../../shared/page-header.component';
import { EmptyStateComponent } from '../../shared/empty-state.component';

@Component({selector:'cq-audit',standalone:true,imports:[DatePipe,PageHeaderComponent,EmptyStateComponent],templateUrl:'./audit.component.html',styleUrl:'./audit.component.css'})
export class AuditComponent {
  private readonly service=inject(AuditService);items:Activity[]=[];loading=true;error='';
  constructor(){this.load()}load(){this.loading=true;this.service.list().subscribe({next:d=>{this.items=d??[];this.loading=false},error:e=>{this.error=e?.error?.detail||'Unable to load audit/activity data.';this.loading=false}})}
}
