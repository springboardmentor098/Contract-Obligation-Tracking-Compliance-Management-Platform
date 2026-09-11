import { Component, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { ReportService } from '../../core/services/report.service';
import { DashboardService } from '../../core/services/dashboard.service';
import { DashboardSummary } from '../../core/models/models';
import { PageHeaderComponent } from '../../shared/page-header.component';

@Component({selector:'cq-reports',standalone:true,imports:[PageHeaderComponent,DecimalPipe],templateUrl:'./reports.component.html',styleUrl:'./reports.component.css'})
export class ReportsComponent {
  private readonly dashboard=inject(DashboardService);private readonly reports=inject(ReportService);
  data?:DashboardSummary;loading=true;error='';
  constructor(){this.load()}
  load(){this.loading=true;this.dashboard.getSummary().subscribe({next:d=>{this.data=d;this.loading=false},error:e=>{this.error=e?.error?.detail||'Unable to load analytics.';this.loading=false}})}
  entries(x:Record<string,number>|undefined){return Object.entries(x??{})}
  total(x:Record<string,number>|undefined){return Object.values(x??{}).reduce((a,b)=>a+b,0)}
}
