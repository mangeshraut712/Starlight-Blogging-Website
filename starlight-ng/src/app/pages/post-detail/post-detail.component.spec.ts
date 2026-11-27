import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';

import { PostDetailComponent } from './post-detail.component';
import { PostService } from 'src/app/services/post.service';
import { UserService } from 'src/app/services/user.service';
import { AuthService } from 'src/app/services/auth.service';
import { MetaService } from 'src/app/services/meta.service';

describe('PostDetailComponent getReadingTime()', () => {
  let component: PostDetailComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [PostDetailComponent],
      providers: [
        { provide: ActivatedRoute, useValue: { params: of({}) } },
        { provide: Router, useValue: { navigate: () => Promise.resolve(true) } },
        { provide: PostService, useValue: {} },
        { provide: UserService, useValue: {} },
        { provide: AuthService, useValue: { isLoggedIn: () => false, getUid: (): string | null => null } },
        { provide: MetaService, useValue: { setPageMeta: () => {}, resetMeta: () => {} } }
      ]
    })
      .overrideComponent(PostDetailComponent, { set: { template: '' } })
      .compileComponents();

    const fixture = TestBed.createComponent(PostDetailComponent);
    component = fixture.componentInstance;
  });

  it('prefers the backend-provided reading time when present', () => {
    component.post.reading_minutes = 7;
    component.post.content = 'word '.repeat(1000);
    expect(component.getReadingTime()).toBe(7);
  });

  it('rounds the word count up to the nearest 200-word minute', () => {
    component.post.content = Array(200).fill('word').join(' ');
    expect(component.getReadingTime()).toBe(1);
    component.post.content = Array(201).fill('word').join(' ');
    expect(component.getReadingTime()).toBe(2);
  });

  it('strips HTML before counting words so tags never inflate the estimate', () => {
    component.post.content = `${Array(150).fill('<b> </b>').join(' ')} ${Array(100).fill('word').join(' ')}`;
    expect(component.getReadingTime()).toBe(1);
  });

  it('clamps tag-only content to a one minute estimate', () => {
    component.post.content = '<p><br></p>';
    expect(component.getReadingTime()).toBe(1);
  });
});
