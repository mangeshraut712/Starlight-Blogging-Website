import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs';
import { AuthGuard } from './auth.guard';
import { AuthService } from './auth.service';

describe('AuthGuard', () => {
  let guard: AuthGuard;
  let authService: jasmine.SpyObj<AuthService>;

  beforeEach(() => {
    authService = jasmine.createSpyObj('AuthService', ['isLoggedIn', 'validateSession']);
    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      providers: [
        AuthGuard,
        { provide: AuthService, useValue: authService }
      ]
    });
    guard = TestBed.inject(AuthGuard);
  });

  it('redirects guests to login with returnUrl', () => {
    authService.isLoggedIn.and.returnValue(false);
    const router = TestBed.inject(Router);
    const result = guard.canActivate({} as any, { url: '/new-post' } as any);
    expect(result).toEqual(router.createUrlTree(['/login'], { queryParams: { returnUrl: '/new-post' } }));
  });

  it('allows authenticated users with valid session', (done) => {
    authService.isLoggedIn.and.returnValue(true);
    authService.validateSession.and.returnValue(of(true));
    const result = guard.canActivate({} as any, { url: '/new-post' } as any);
    if (typeof result === 'object' && 'subscribe' in result) {
      result.subscribe(value => {
        expect(value).toBe(true);
        done();
      });
    } else {
      fail('expected observable');
      done();
    }
  });
});
