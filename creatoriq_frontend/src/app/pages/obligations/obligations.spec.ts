import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Obligations } from './obligations';

describe('Obligations', () => {
  let component: Obligations;
  let fixture: ComponentFixture<Obligations>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Obligations],
    }).compileComponents();

    fixture = TestBed.createComponent(Obligations);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
