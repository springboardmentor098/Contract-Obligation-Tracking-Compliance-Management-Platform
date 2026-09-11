import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { ContractService } from '../../core/services/contract.service';
import { Contract } from '../../core/models/models';
import { PageHeaderComponent } from '../../shared/page-header.component';
import { StatusComponent } from '../../shared/status.component';
import { EmptyStateComponent } from '../../shared/empty-state.component';
import { DatePipe } from '@angular/common';

@Component({
  selector:'cq-contracts', standalone:true,
  imports:[ReactiveFormsModule,FormsModule,DatePipe,PageHeaderComponent,StatusComponent,EmptyStateComponent],
  templateUrl:'./contracts.component.html', styleUrl:'./contracts.component.css'
})
export class ContractsComponent {
  private readonly service=inject(ContractService); private readonly fb=inject(FormBuilder);
  contracts:Contract[]=[]; filtered:Contract[]=[]; loading=true; error=''; showForm=false; editing?:Contract; query=''; status='';
  form=this.fb.nonNullable.group({title:['',Validators.required],contract_number:['',Validators.required],category:['Vendor Contract',Validators.required],status:['Draft',Validators.required],start_date:[''],end_date:['']});
  categories=['Employment Contract','Vendor Contract','Service Agreement','Lease','Purchase','Partnership','Confidentiality'];
  statuses=['Draft','Under Review','Approved','Active','Expired','Terminated'];
  constructor(){this.load()}
  load(){this.loading=true;this.service.list().subscribe({next:d=>{this.contracts=d??[];this.apply();this.loading=false},error:e=>{this.error=e?.error?.detail||'Unable to load contracts.';this.loading=false}})}
  apply(){const q=this.query.toLowerCase();this.filtered=this.contracts.filter(c=>(!q||c.title.toLowerCase().includes(q)||c.contract_number.toLowerCase().includes(q))&&(!this.status||c.status===this.status))}
  open(c?:Contract){this.editing=c;if(c)this.form.patchValue({...c,start_date:c.start_date?.slice(0,10)??'',end_date:c.end_date?.slice(0,10)??''});else this.form.reset({title:'',contract_number:'',category:'Vendor Contract',status:'Draft',start_date:'',end_date:''});this.showForm=true}
  save(){if(this.form.invalid){this.form.markAllAsTouched();return}const v=this.form.getRawValue();const req=this.editing?this.service.update(this.editing.id,v):this.service.create(v);req.subscribe({next:()=>{this.showForm=false;this.load()},error:e=>this.error=e?.error?.detail||'Could not save contract.'})}
  remove(c:Contract){if(!confirm(`Delete ${c.title}?`))return;this.service.remove(c.id).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Could not delete contract.'})}
  statusUpdate(c:Contract,s:string){this.service.updateStatus(c.id,s).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Status update failed.'})}
}
