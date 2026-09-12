import { TestBed } from '@angular/core/testing';

import { Obligations } from './obligations';

describe('Obligations', () => {
  let service: Obligations;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Obligations);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
