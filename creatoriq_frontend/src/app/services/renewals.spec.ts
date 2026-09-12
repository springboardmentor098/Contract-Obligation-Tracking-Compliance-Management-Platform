import { TestBed } from '@angular/core/testing';

import { Renewals } from './renewals';

describe('Renewals', () => {
  let service: Renewals;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Renewals);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
