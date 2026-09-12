import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Renewals } from './renewals';

describe('Renewals', () => {
  let component: Renewals;
  let fixture: ComponentFixture<Renewals>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Renewals],
    }).compileComponents();

    fixture = TestBed.createComponent(Renewals);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
