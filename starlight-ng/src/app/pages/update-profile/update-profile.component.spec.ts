import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AuthService } from 'src/app/services/auth.service';

import { UpdateProfileComponent } from './update-profile.component';

describe('UpdateProfileComponent', () => {
  let component: UpdateProfileComponent;
  let fixture: ComponentFixture<UpdateProfileComponent>;

  beforeEach(async () => {
    spyOn(AuthService.prototype, 'getUid').and.returnValue('7');
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, FormsModule],
      declarations: [ UpdateProfileComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateProfileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('keeps the loaded bio and username when saving the profile', () => {
    const http = TestBed.inject(HttpTestingController);
    spyOn(TestBed.inject(Router), 'navigate').and.resolveTo(true);
    http.expectOne((req) => req.method === 'GET' && req.url.endsWith('/api/users/7')).flush({
      id: 7, first: 'Ada', last: 'Lovelace', bio: 'Writes about engines', username: 'ada',
    });

    component.updateProfile();

    const put = http.expectOne((req) => req.method === 'PUT' && req.url.endsWith('/api/update-profile'));
    expect(put.request.body.bio).toBe('Writes about engines');
    expect(put.request.body.username).toBe('ada');
    put.flush({ message: 'ok' });
  });
});
