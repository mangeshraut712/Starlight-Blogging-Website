import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-recovery',
  templateUrl: './recovery.component.html',
  styleUrls: ['./recovery.component.css']
})
export class RecoveryComponent {
  errorMessage:string = "";
  email:string = "";
  user_id:number;
  
  constructor(private router: Router, private authService: AuthService) {}
  
  recover() {
    this.authService.forgotPassword(this.email).subscribe(
      (response) => {
        this.user_id = response.user_id
        console.log(this.user_id);
        this.router.navigate(['change-password', this.user_id]);
      },
      (error) => {
        console.log("Error: " + error);
        this.errorMessage = "This email does not exist in our database.";
      }
    )
    
  }

}
