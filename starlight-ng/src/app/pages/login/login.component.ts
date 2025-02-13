import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email: string = "";
  password: string = "";
  errorMessage: string ="";

  constructor (
    private router:Router, 
    private authService: AuthService, 
    private http: HttpClient
  ){}

  ngOnInit(): void {
    console.log(this.authService.test());
  }

  gotoHome(){
    this.authService.login(this.email, this.password)
    .subscribe(
      (response: any) => {
        console.log(response);
        const token = response.token;
        const uid= response.uid;
        this.authService.setUid(uid);
        this.authService.setToken(token);
        this.router.navigate(['homepage-posts']);
      },
      (error: any) => {
        console.log('Login failed: ', error);
        this.errorMessage = 'Invalid username or password';
      }
    );
  }
}
