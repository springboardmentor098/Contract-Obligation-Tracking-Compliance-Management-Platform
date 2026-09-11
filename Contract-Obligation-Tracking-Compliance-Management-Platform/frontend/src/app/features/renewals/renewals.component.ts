import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { RenewalService } from '../../core/services/renewal.service';
import { Renewal } from '../../core/models/models';
import { PageHeaderComponent } from '../../shared/page-header.component';
import { StatusComponent } from '../../shared/status.component';
import { EmptyStateComponent } from '../../shared/empty-state.component';

@Component({selector:'cq-renewals',standalone:true,imports:[FormsModule,DatePipe,PageHeaderComponent,StatusComponent,EmptyStateComponent],templateUrl:'./renewals.component.html',styleUrl:'./renewals.component.css'})
export class RenewalsComponent {
  private readonly service=inject(RenewalService); items:Renewal[]=[];filtered:Renewal[]=[];query='';status='';loading=true;error='';
  statuses=['Upcoming','In Progress','Renewed','Expired','Cancelled'];
  constructor(){this.load()} load(){this.loading=true;this.service.list().subscribe({next:d=>{this.items=d??[];this.apply();this.loading=false},error:e=>{this.error=e?.error?.detail||'Unable to load renewals.';this.loading=false}})}
  apply(){const q=this.query.toLowerCase();this.filtered=this.items.filter(x=>(!q||String(x.contract_id).includes(q))&&(!this.status||x.status===this.status))}
  change(x:Renewal,s:string){this.service.status(x.id,s).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Renewal status update failed.'})}
}
