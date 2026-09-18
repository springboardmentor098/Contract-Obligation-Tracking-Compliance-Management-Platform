import { Component, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { NotificationService } from '../../core/services/notification.service';
import { Notification } from '../../core/models/models';
import { PageHeaderComponent } from '../../shared/page-header.component';
import { EmptyStateComponent } from '../../shared/empty-state.component';

@Component({selector:'cq-notifications',standalone:true,imports:[DatePipe,PageHeaderComponent,EmptyStateComponent],templateUrl:'./notifications.component.html',styleUrl:'./notifications.component.css'})
export class NotificationsComponent {
  private readonly service=inject(NotificationService);items:Notification[]=[];loading=true;error='';
  constructor(){this.load()}load(){this.loading=true;this.service.list().subscribe({next:d=>{this.items=d??[];this.loading=false},error:e=>{this.error=e?.error?.detail||'Unable to load notifications.';this.loading=false}})}
  isUnread(x:Notification){return !(x.is_read??x.read??false)}
  markRead(x:Notification){this.service.read(x.id).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Could not mark notification as read.'})}
}
