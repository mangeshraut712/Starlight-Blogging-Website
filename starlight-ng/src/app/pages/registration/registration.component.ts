import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.css']
})
export class RegistrationComponent implements OnInit {
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
  first: string = '';
  last: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;
  registrationForm: FormGroup;

  constructor(
    private router: Router, 
    private authService: AuthService,
    private formBuilder: FormBuilder
  ) {
    this.registrationForm = this.formBuilder.group({
      first: ['', [Validators.required, Validators.minLength(2)]],
      last: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    // Redirect if already logged in
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/homepage-posts']);
    }
  }
  
  onRegister(): void {
    // Clear previous error messages
    this.errorMessage = '';

    // Validate form fields manually
    if (!this.first || this.first.trim().length < 2) {
      this.errorMessage = 'First name must be at least 2 characters long.';
      return;
    }

    if (!this.last || this.last.trim().length < 2) {
      this.errorMessage = 'Last name must be at least 2 characters long.';
      return;
    }

    if (!this.email || !this.isValidEmail(this.email)) {
      this.errorMessage = 'Please enter a valid email address.';
      return;
    }

    if (!this.password || this.password.length < 8) {
      this.errorMessage = 'Password must be at least 8 characters long.';
      return;
    }

    if (this.password !== this.confirmPassword) {
      this.errorMessage = 'Passwords do not match.';
      return;
    }

    this.isLoading = true;

    this.authService.register(this.email, this.first, this.last, this.password)
      .subscribe({
        next: (response: any) => {
          this.isLoading = false;
          console.log('Registration successful:', response);
          this.router.navigate(['/login']);
        },
        error: (error: any) => {
          this.isLoading = false;
          console.error('Registration failed:', error);
          
          if (error.status === 409) {
            this.errorMessage = 'This email is already registered. Please use a different email or try logging in.';
          } else if (error.status === 400) {
            this.errorMessage = 'Please check your information and try again.';
          } else if (error.status === 0 || error.name === 'HttpErrorResponse') {
            this.errorMessage = 'Backend server is not running. Please start the backend server on port 8080.';
          } else if (error.status === 500) {
            this.errorMessage = 'Server error. Please try again later.';
          } else {
            this.errorMessage = `Registration failed: ${error.message || 'Unknown error'}. Please try again.`;
          }
        }
      });
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}
