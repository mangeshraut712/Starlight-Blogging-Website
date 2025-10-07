import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }),
  withCredentials: true
};

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly BASE_URL: string = environment.apiUrl || 'http://localhost:8080';
  private readonly UID_KEY = 'starlight_uid';
  private readonly TOKEN_KEY = 'starlight_auth_token';

  constructor(private http: HttpClient) {}

  /**
   * Set user ID in localStorage
   */
  setUid(uid: string): void {
    if (uid) {
      localStorage.setItem(this.UID_KEY, uid);
    }
  }

  /**
   * Get user ID from localStorage
   */
  getUid(): string | null {
    return localStorage.getItem(this.UID_KEY);
  }

  /**
   * Check if user is logged in
   */
  isLoggedIn(): boolean {
    const token = this.getToken();
    return token !== null && token !== '';
  }

  /**
   * Get authentication token from localStorage
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Set authentication token in localStorage
   */
  setToken(token: string): void {
    if (token) {
      localStorage.setItem(this.TOKEN_KEY, token);
    }
  }

  /**
   * Clear all authentication data
   */
  clearAuthData(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.UID_KEY);
  }

  /**
   * Login user with email and password
   */
  login(email: string, password: string): Observable<any> {
    const loginData = { email, password };
    return this.http.post<any>(`${this.BASE_URL}/api/login`, loginData, httpOptions)
      .pipe(
        tap(response => {
          if (response && response.token && response.uid) {
            this.setToken(response.token);
            this.setUid(response.uid);
          }
        }),
        catchError(this.handleError)
      );
  }

  /**
   * Register new user
   */
  register(email: string, first: string, last: string, password: string): Observable<any> {
    const registerData = { email, first, last, password };
    return this.http.post<any>(`${this.BASE_URL}/api/register`, registerData, httpOptions)
      .pipe(
        catchError(this.handleRegisterError)
      );
  }

  /**
   * Send forgot password email
   */
  forgotPassword(email: string): Observable<any> {
    return this.http.post<any>(`${this.BASE_URL}/api/forgot_password`, { email }, httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Reset user password
   */
  resetPassword(userId: number, newPassword: string, confirmPassword: string): Observable<any> {
    const resetData = {
      user_id: userId,
      new_password: newPassword,
      confirm_password: confirmPassword
    };
    return this.http.post<any>(`${this.BASE_URL}/api/reset_password`, resetData, httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Logout user
   */
  logout(): Observable<any> {
    this.clearAuthData();
    return this.http.get<any>(`${this.BASE_URL}/api/logout`, httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Get user data
   */
  getData(): Observable<any> {
    return this.http.get<any>(`${this.BASE_URL}/api/data`, httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Handle registration errors specifically
   */
  private handleRegisterError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'Registration failed';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Registration Client Error: ${error.error.message}`;
    } else {
      // Server-side error
      switch (error.status) {
        case 400:
          errorMessage = 'Invalid registration data. Please check your input.';
          break;
        case 401:
          // Special case for existing user
          if (error.error && error.error.error) {
            errorMessage = error.error.error; // "This email belongs to an already existing user"
          } else {
            errorMessage = 'Registration unauthorized. Please try a different email.';
          }
          break;
        case 409:
          errorMessage = 'User with this email already exists. Please use a different email or try logging in.';
          break;
        case 500:
          errorMessage = 'Server error during registration. Please try again later.';
          break;
        default:
          errorMessage = `Registration failed: ${error.status} - ${error.message || 'Unknown error'}`;
      }
    }

    console.error('Registration Error:', errorMessage, error);
    return throwError(() => new Error(errorMessage));
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unexpected error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Server-side error
      switch (error.status) {
        case 400:
          errorMessage = 'Bad request. Please check your input.';
          break;
        case 401:
          errorMessage = 'Unauthorized. Please check your credentials.';
          break;
        case 403:
          errorMessage = 'Forbidden. You do not have permission to access this resource.';
          break;
        case 404:
          errorMessage = 'Resource not found.';
          break;
        case 409:
          errorMessage = 'Conflict. The resource already exists.';
          break;
        case 500:
          errorMessage = 'Internal server error. Please try again later.';
          break;
        case 0:
          errorMessage = 'Network error. Please check your connection.';
          break;
        default:
          errorMessage = `Server Error: ${error.status} - ${error.message}`;
      }
    }
    
    console.error('AuthService Error:', errorMessage, error);
    return throwError(() => new Error(errorMessage));
  }
}
