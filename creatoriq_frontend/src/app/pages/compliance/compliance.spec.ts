import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Compliance } from './compliance';

describe('Compliance', () => {
  let component: Compliance;
  let fixture: ComponentFixture<Compliance>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Compliance],
    }).compileComponents();

    fixture = TestBed.createComponent(Compliance);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
