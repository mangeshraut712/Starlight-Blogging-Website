import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.css']
})
export class ChangePasswordComponent implements OnInit {
  newPassword = '';
  confirmPassword = '';
  resetToken = '';
  errorMessage = '';

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.resetToken = params['token'] || '';
    });
  }

  changePassword(): void {
    if (!this.resetToken) {
      this.errorMessage = 'Invalid or missing reset link. Please request a new one.';
      return;
    }
    if (this.newPassword.length < 8) {
      this.errorMessage = 'Password must be at least 8 characters.';
      return;
    }
    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage = 'Passwords do not match.';
      return;
    }

    this.authService.resetPassword(this.resetToken, this.newPassword, this.confirmPassword).subscribe({
      next: () => this.router.navigate(['/login']),
      error: (error) => {
        this.errorMessage = error.message || 'Unable to reset password.';
      }
    });
  }
}
