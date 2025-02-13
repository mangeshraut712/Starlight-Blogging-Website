import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HomepagePostsComponent } from './homepage-posts.component';

describe('HomepagePostsComponent', () => {
  let component: HomepagePostsComponent;
  let fixture: ComponentFixture<HomepagePostsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HomepagePostsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HomepagePostsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
