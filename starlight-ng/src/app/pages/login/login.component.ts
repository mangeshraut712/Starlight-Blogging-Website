import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  email: string = '';
  password: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;
  loginForm: FormGroup;

  constructor(
    private router: Router,
    private authService: AuthService,
    private formBuilder: FormBuilder
  ) {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngOnInit(): void {
    // Redirect if already logged in
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/homepage-posts']);
    }
  }

  onLogin(): void {
    // Clear previous error messages
    this.errorMessage = '';

    // Validate form fields manually
    if (!this.email || !this.isValidEmail(this.email)) {
      this.errorMessage = 'Please enter a valid email address.';
      return;
    }

    if (!this.password || this.password.length < 6) {
      this.errorMessage = 'Password must be at least 6 characters long.';
      return;
    }

    this.isLoading = true;

    this.authService.login(this.email, this.password)
      .subscribe({
        next: (response: any) => {
          this.isLoading = false;
          if (response && response.token && response.uid) {
            this.authService.setUid(response.uid);
            this.authService.setToken(response.token);
            this.router.navigate(['/homepage-posts']);
          } else {
            this.errorMessage = 'Invalid response from server';
          }
        },
        error: (error: any) => {
          this.isLoading = false;
          console.error('Login failed:', error);
          
          if (error.status === 401) {
            this.errorMessage = 'Invalid email or password';
          } else if (error.status === 0 || error.name === 'HttpErrorResponse') {
            this.errorMessage = 'Backend server is not running. Please start the backend server on port 8080.';
          } else if (error.status === 500) {
            this.errorMessage = 'Server error. Please try again later.';
          } else {
            this.errorMessage = `Login failed: ${error.message || 'Unknown error'}. Please try again.`;
          }
        }
      });
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}
