import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.css']
})
export class RegistrationComponent {
  email: string = "";
  password: string = "";
  first: string = "";
  last: string = "";
  errorMessage: string ="";

  constructor (private router:Router, private authService: AuthService){}
  
  login() {
    this.authService.register(this.email, this.first, this.last, this.password)
      .subscribe(
        (response: any) => {
          console.log(response);
          this.router.navigate(['login']);
        },
        (error: any) => {
          console.log(error);
          this.errorMessage = 'This email belongs to an already existing user';
        }
      );
  }

}
