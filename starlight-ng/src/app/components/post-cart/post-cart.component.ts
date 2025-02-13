import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { PopUpComponent } from '../pop-up/pop-up.component';
import { ActivatedRoute, Router } from '@angular/router';
import { DatePipe } from '@angular/common';
// classes
import { Post } from 'src/app/models/post';
import { User } from 'src/app/models/user';
import { Comment } from 'src/app/models/comment';
// services
import { UserService } from 'src/app/services/user.service';
import { PostService } from 'src/app/services/post.service';
import { AuthService } from 'src/app/services/auth.service';


@Component({
  selector: 'app-post-cart',
  templateUrl: './post-cart.component.html',
  styleUrls: ['./post-cart.component.css']
})
export class PostCartComponent {

  @Input() currentPost: Post;

  title: string = '';
  isLiked:boolean = false;
  likes: number =0;
  seeComments:boolean=false;
  user: User;
  posts: Post[];
  comments: Comment[];
  newComment: Comment;
  post: Post;
  body:string = "";
  
    
  constructor(
    private dialogRef : MatDialog,
    private userService: UserService, 
    private postService: PostService,
    private router: Router,
    private route: ActivatedRoute,
    private datePipe: DatePipe,
    private authService: AuthService
  ) {
    this.post= new Post();
    this.user = new User();
    this.posts = [];
    this.comments = [];
    this.newComment = new Comment();
    this.currentPost = new Post();
  }

  ngOnInit(){
    this.getUser();

    this.getPostLikes();
    this.getPostComments();

    console.log("currentPost created_at = " + this.currentPost.created_at);
    this.currentPost.created_at = this.datePipe.transform(this.currentPost.created_at, 'MM/dd/yyyy');
    // this.newComment.created_at = this.datePipe.transform(this.newComment.created_at, 'MM/dd/yy HH:mm');

  }

  getUser(): void {
    const uid = Number(this.authService.getUid());
    this.userService.getUserById(uid).subscribe(
      (data) => {
        this.user = data;
      }
    )
	}

  getPost(): void {
    this.route.params.subscribe(params => {
      const postId = params['id'];
      this.postService.getPost(postId).subscribe(post => {
        this.currentPost = post;
      });
    });
  }

  getPostLikes(): void {
    this.postService.getPostLikes(this.currentPost.id).subscribe(
      (likes) => {
        this.isLiked = likes.some(like => like.user_id === this.user.id);
      }
    )
  }

  getPostComments():void {
    this.postService.getPostComments(this.currentPost.id).subscribe(comments => {
      console.log(comments);
      this.comments = comments;
    });
  }

  deletePost(post: Post) {
    const dialog = this.dialogRef.open(PopUpComponent);
    dialog.afterClosed().subscribe(result => {
      if (result) {
        this.postService.deletePost(post.id).subscribe(
          (response) => {
            console.log("deleting post: "+response);
            this.posts = this.posts.filter(p => p.id !== post.id);
          },
          (error) => {
            console.log("Error deleting post ", error);
          }
        );
        window.location.reload();
        // this.router.navigate(['homepage-posts']);
      }
    });
  }

  showComments(){
    this.seeComments=!this.seeComments;
  }

  submitComment() {
    console.log('Submitting comment');
    this.postService.commentPost(this.currentPost.id, this.newComment.body).subscribe(
      (comment) => {
        console.log(comment);
        this.comments.push(comment);
        // this.postService.getPostComments(this.currentPost.id).subscribe(comments => this.comments = comments);
        this.newComment.body = "";
      },
      (error) => {
        console.log(error);
      }
    )
  }

  toggleLike() {
    if(this.isLiked){
      // Unlike the post
      this.postService.likePost(this.currentPost.id).subscribe(
        (response) => {
          console.log("Unliking post: ", response);
          this.currentPost.likes -= 1;
          this.isLiked = false;
        }
      );
    } else {
      // Like the post
      this.postService.likePost(this.currentPost.id).subscribe(
        (response) => {
          console.log("Liking post: ", response);
          this.currentPost.likes += 1;
          this.isLiked = true;
        }
      );
    }
  }
}
