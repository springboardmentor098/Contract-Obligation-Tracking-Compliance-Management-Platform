import { TestBed } from '@angular/core/testing';

import { Contracts } from './contracts';

describe('Contracts', () => {
  let service: Contracts;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Contracts);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
