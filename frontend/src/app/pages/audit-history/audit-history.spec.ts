import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AuditHistory } from './audit-history';

describe('AuditHistory', () => {
  let component: AuditHistory;
  let fixture: ComponentFixture<AuditHistory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AuditHistory],
    }).compileComponents();

    fixture = TestBed.createComponent(AuditHistory);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
