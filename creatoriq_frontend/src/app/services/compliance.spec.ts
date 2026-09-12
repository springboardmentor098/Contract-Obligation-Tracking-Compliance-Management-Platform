import { TestBed } from '@angular/core/testing';

import { Compliance } from './compliance';

describe('Compliance', () => {
  let service: Compliance;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Compliance);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
