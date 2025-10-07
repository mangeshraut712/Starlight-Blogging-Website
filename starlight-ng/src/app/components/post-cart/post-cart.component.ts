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
  styleUrls: ['./post-cart.component.css'],
  providers: [DatePipe]
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
  successMessage: string = "";
  isExpanded = false;
  
    
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
      this.comments = comments;
    });
  }

  deletePost(post: Post) {
    const dialog = this.dialogRef.open(PopUpComponent, {
      data: { message: 'Are you sure you want to delete this post?' }
    });

    dialog.afterClosed().subscribe(result => {
      if (result) {
        this.postService.deletePost(post.id).subscribe(
          (response) => {
            this.successMessage = 'Post deleted successfully!';
            setTimeout(() => this.successMessage = '', 3000);
            window.location.reload();
          },
          (error) => {
            console.log("Error deleting post ", error);
          }
        );
      }
    });
  }

  isOwnPost(): boolean {
    return this.user && this.user.id === this.currentPost.author_id;
  }

  showComments(){
    this.seeComments=!this.seeComments;
  }

  submitComment() {
    if (!this.newComment.body || this.newComment.body.trim() === '') {
      return; // Don't submit empty comments
    }

    this.postService.commentPost(this.currentPost.id, this.newComment.body.trim()).subscribe(
      (comment: Comment) => {
        this.comments.unshift(comment); // Add to beginning of array for newest first
        this.newComment.body = "";
        this.successMessage = 'Comment added successfully!';
        setTimeout(() => this.successMessage = '', 3000);
      },
      (error) => {
        console.log('Error posting comment:', error);
        this.successMessage = 'Failed to add comment. Please try again.';
        setTimeout(() => this.successMessage = '', 3000);
      }
    )
  }

  toggleLike() {
    this.postService.likePost(this.currentPost.id).subscribe(
      (response: any) => {
        // Toggle the liked state
        this.isLiked = !this.isLiked;
        // Refresh likes from server to get accurate count
        this.postService.getPostLikes(this.currentPost.id).subscribe(
          (likes) => {
            this.currentPost.likes = likes.length;
          },
          (error) => {
            console.log('Error getting likes:', error);
          }
        );
      },
      (error) => {
        console.log('Error toggling like:', error);
      }
    );
  }

  toggleReadMore() {
    this.isExpanded = !this.isExpanded;
  }
}
