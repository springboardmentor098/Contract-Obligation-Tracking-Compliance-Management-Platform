import { TestBed } from '@angular/core/testing';

import { Reports } from './reports';

describe('Reports', () => {
  let service: Reports;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Reports);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
