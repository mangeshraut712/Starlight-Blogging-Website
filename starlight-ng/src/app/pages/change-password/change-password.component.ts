import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.css']
})
export class ChangePasswordComponent {
  newPassword:string = "";
  confirmPassword:string = "";
  userId:number;
  errorMessage:string = "";

  constructor(private router: Router, private route: ActivatedRoute, private authService: AuthService) {}
  
  ngOnInit() {
    this.route.params.subscribe(params => {
      this.userId = params['user_id'];
    });
  }

  changePassword() {
    this.authService.resetPassword(this.userId, this.newPassword, this.confirmPassword).subscribe(
      (response) => {
        console.log(response);
        this.router.navigate(['login']);
      },
      (error) => {
        console.log(error);
        this.errorMessage = error.error.message;
      }
    )
  }

}
