import { Component, Input, OnInit,  } from '@angular/core';
import { Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';
// classes
import { User } from 'src/app/models/user';
import { AuthService } from 'src/app/services/auth.service';
// services
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-update-profile',
  templateUrl: './update-profile.component.html',
  styleUrls: ['./update-profile.component.css']
})
export class UpdateProfileComponent implements OnInit {

  user: User;
  message: string ="";
  oldPassword:string = "";
  @Input() url: string | ArrayBuffer | null | undefined;
Update: any;


  constructor(private router: Router, private route: ActivatedRoute, private userService: UserService, private authService: AuthService) {
    this.user = new User();
  }

  ngOnInit() {
    this.getUser();
	}

	// getUser(userId: number): void {
	getUser(): void {
    const uid = Number(this.authService.getUid());
    this.userService.getUserById(uid).subscribe(
      (data) => {
        // this.user = data;
        this.user.email = data.email;
        this.user.first = data.first;
        this.user.last = data.last;
        this.user.id = data.id;
        console.log("gerUserData return: ", this.user);
      }
    )
	}
	
  
  goToHome() {
    this.router.navigate(['homepage-posts']);
  }

  updateProfile() {
    this.userService.updateUser(this.user).subscribe(
      (response:any) => {
        console.log("updateProfile response = " + response.message);
        // alert('Profile updated successfully');
        this.message = response.message;
        this.router.navigate(['update-profile']);
      },
      (error:any) => {
        console.log('Update failed: ', error)
      }
    );
  }
  // updateProfile(): void {		
	// 	this.userService.updateUser(this.user).subscribe(success=> {this.goBack();});
	// }

  onSelectFile(event:any) {
    if (event.target.files && event.target.files[0]) {
      var reader = new FileReader();

      reader.readAsDataURL(event.target.files[0]); // read file as data url

      reader.onload = (event) => { // called once readAsDataURL is completed
        if(event.target) {
          this.url = event.target.result;
        }
      }
    }
  }

}
