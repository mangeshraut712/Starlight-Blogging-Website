import { Component,Inject } from '@angular/core';
import { Router } from '@angular/router';
import { Post } from 'src/app/models/post';
import { User } from 'src/app/models/user';
import { AuthService } from 'src/app/services/auth.service';
import { DataService } from 'src/app/services/data.service';
import { PostService } from 'src/app/services/post.service';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-new-post',
  templateUrl: './new-post.component.html',
  styleUrls: ['./new-post.component.css']
})


export class NewPostComponent {

  communityList:string[];

  user:User;
  title:string="";
  content:string="";
  posts: Post[];
  newPost:Post;
  errorMessage:string = "";
  
  constructor(
    private router:Router, 
    private data: DataService, 
    private postService:PostService, 
    private userService: UserService,
    private authService: AuthService
  ){

    this.user= new User();
    this.newPost = new Post();
    this.posts = [];
    this.communityList= this.data.communityList;

    // this.newPost.date = this.getCurrentDate();
  }

  ngOnInit(){
    this.getUser();
  }
  
  getUser(): void {
    const uid = Number(this.authService.getUid());
    this.userService.getUserById(uid).subscribe(
      (data) => {
        this.user = data;
      }
    )
	}

  getPosts(): void {
    this.postService.getAllPosts()
    .subscribe( posts => this.posts = posts);
  }


  cancelNewPost(event:any){
   this.router.navigate(['homepage-posts']);
  }

  createNewPost() {
    if(this.newPost.label == null){
      this.errorMessage = "You cannot post without selecting a label.";
      return;
    }
    
    this.postService.addPost(this.newPost)
    .subscribe(
      (data) => {
        console.log("Post created = " + data);
        console.log("newPost.author name = " + this.newPost.author_name);
        this.posts.push(this.newPost);
        this.router.navigate(['homepage-posts']);
      },
      (error) => {
        console.log('Create post failed: ', error);
      }
    )
  }


  getCurrentDate(): string {
    const date = new Date();

    let day = date.getDate();
    let month = date.getMonth() + 1;
    let year = date.getFullYear();
    // This arrangement can be altered based on how we want the date's format to appear.
    let currentDate = `${month}/${day}/${year}`;

    return currentDate;
  }
}
