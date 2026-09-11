import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { ObligationService } from '../../core/services/obligation.service';
import { Obligation } from '../../core/models/models';
import { PageHeaderComponent } from '../../shared/page-header.component';
import { StatusComponent } from '../../shared/status.component';
import { EmptyStateComponent } from '../../shared/empty-state.component';

@Component({selector:'cq-obligations',standalone:true,imports:[FormsModule,DatePipe,PageHeaderComponent,StatusComponent,EmptyStateComponent],templateUrl:'./obligations.component.html',styleUrl:'./obligations.component.css'})
export class ObligationsComponent {
  private readonly service=inject(ObligationService); items:Obligation[]=[]; filtered:Obligation[]=[]; query='';status='';loading=true;error='';
  statuses=['Pending','In Progress','Delayed','Overdue','Completed'];
  constructor(){this.load()} load(){this.loading=true;this.service.list().subscribe({next:d=>{this.items=d??[];this.apply();this.loading=false},error:e=>{this.error=e?.error?.detail||'Unable to load obligations.';this.loading=false}})}
  apply(){const q=this.query.toLowerCase();this.filtered=this.items.filter(x=>(!q||x.title.toLowerCase().includes(q)||String(x.contract_id).includes(q))&&(!this.status||x.status===this.status))}
  change(x:Obligation,s:string){this.service.status(x.id,s).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Status update failed.'})}
}
