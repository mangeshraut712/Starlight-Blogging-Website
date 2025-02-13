import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Router } from '@angular/router';
// classes
import { Post } from 'src/app/models/post';
// services
import { AuthService } from 'src/app/services/auth.service';
import { DataService } from 'src/app/services/data.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})

export class NavbarComponent {
  @Input() title: string = '';
  @Input() icon:string='';
  @Input() frontpage:string='';
  @Input() path:string="";
  @Output()messageEvent= new EventEmitter();

  communities:boolean=false;
  communityList:string[];
  post: Post;

  constructor (
    private router:Router, 
    private data: DataService, 
    private authService: AuthService
  ){
    this.communityList= data.communityList;
    this.post= new Post();
  }

  ngOnInit(){
  }
  
  gotoHome(){
    this.router.navigate(['homepage-posts']);
  }

  goToNewPost(){
    this.router.navigate(['new-post']);
  }

  displayCommunities(event:any){
    this.communities=!this.communities;
  }

  sendCommunityTag(tag:string){
    this.router.navigate(['community', tag]);
  }

  logout() {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/']);
    });
  }

}
