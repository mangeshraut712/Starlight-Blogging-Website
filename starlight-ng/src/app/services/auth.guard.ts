import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree, Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(
    _next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | boolean | UrlTree {
    if (!this.authService.isLoggedIn()) {
      return this.redirectToLogin(state.url);
    }

    return this.authService.validateSession().pipe(
      map(valid => valid || this.redirectToLogin(state.url)),
      catchError(() => of(this.redirectToLogin(state.url)))
    );
  }

  private redirectToLogin(returnUrl: string): UrlTree {
    return this.router.createUrlTree(['/login'], {
      queryParams: { returnUrl: returnUrl !== '/login' ? returnUrl : undefined }
    });
  }
}
