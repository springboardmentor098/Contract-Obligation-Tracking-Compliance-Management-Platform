import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AuditHistoryComponent } from './audit-history.component';

describe('AuditHistoryComponent', () => {
  let component: AuditHistoryComponent;
  let fixture: ComponentFixture<AuditHistoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AuditHistoryComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AuditHistoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
