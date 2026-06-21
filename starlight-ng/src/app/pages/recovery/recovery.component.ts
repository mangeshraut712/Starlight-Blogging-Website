import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-recovery',
  templateUrl: './recovery.component.html',
  styleUrls: ['./recovery.component.css']
})
export class RecoveryComponent {
  errorMessage = '';
  successMessage = '';
  email = '';

  constructor(private router: Router, private authService: AuthService) {}

  recover(): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.authService.forgotPassword(this.email).subscribe({
      next: (response) => {
        if (response.reset_token) {
          this.router.navigate(['/change-password'], { queryParams: { token: response.reset_token } });
          return;
        }
        this.successMessage = response.message || 'If an account exists, reset instructions have been sent.';
      },
      error: () => {
        this.errorMessage = 'Unable to process request. Please try again later.';
      }
    });
  }
}
