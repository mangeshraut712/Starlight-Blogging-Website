import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CommunityLabelComponent } from './community-label.component';

describe('CommunityLabelComponent', () => {
  let component: CommunityLabelComponent;
  let fixture: ComponentFixture<CommunityLabelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CommunityLabelComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CommunityLabelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
