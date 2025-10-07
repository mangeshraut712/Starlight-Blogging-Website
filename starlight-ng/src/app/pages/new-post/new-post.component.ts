import { Component, OnInit } from '@angular/core';
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
export class NewPostComponent implements OnInit {
  communityList: string[] = [];
  user: User = new User();
  newPost: Post = new Post();
  errorMessage: string = '';
  isLoading: boolean = false;

  // TinyMCE Editor Configuration
  editorConfig = {
    plugins: 'lists link image table code help wordcount',
    toolbar: 'undo redo | blocks | bold italic | alignleft aligncenter alignright | bullist numlist outdent indent | link image | code | help',
    menubar: false,
    branding: false,
    height: 400,
    placeholder: 'Write your post content here...',
    content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; }'
  };

  constructor(
    private router: Router,
    private data: DataService,
    private postService: PostService,
    private userService: UserService,
    private authService: AuthService
  ) {
    this.communityList = this.data.communityList;
  }

  ngOnInit(): void {
    // Check if user is logged in
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    
    this.getUser();
  }

  getUser(): void {
    const uid = this.authService.getUid();
    if (uid) {
      this.userService.getUserById(Number(uid)).subscribe({
        next: (data) => {
          this.user = data;
          console.log('User loaded:', this.user);
        },
        error: (error) => {
          console.error('Error loading user:', error);
          this.errorMessage = 'Error loading user data. Please try again.';
        }
      });
    } else {
      console.log('No user ID found, redirecting to login');
      this.router.navigate(['/login']);
    }
  }

  cancelNewPost(event: Event): void {
    event.preventDefault();
    this.router.navigate(['/homepage-posts']);
  }

  createNewPost(): void {
    if (this.isLoading) return;

    // Validate form data
    if (!this.validateForm()) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    // Create post object with required fields
    const postData = {
      title: this.newPost.title?.trim() || '',
      content: this.newPost.content?.trim() || '',
      label: this.newPost.label?.trim() || ''
    };

    console.log('Creating post with data:', postData);

    this.postService.addPost(postData).subscribe({
      next: (response) => {
        this.isLoading = false;
        console.log('Post created successfully:', response);
        this.router.navigate(['/homepage-posts']);
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Create post failed:', error);
        
        if (error.status === 401) {
          this.errorMessage = 'You must be logged in to create posts.';
          this.router.navigate(['/login']);
        } else if (error.status === 400) {
          this.errorMessage = 'Please check your post data and try again.';
        } else if (error.status === 0) {
          this.errorMessage = 'Unable to connect to server. Please check your connection.';
        } else {
          this.errorMessage = 'Failed to create post. Please try again.';
        }
      }
    });
  }

  private validateForm(): boolean {
    if (!this.newPost.title || this.newPost.title.trim() === '') {
      this.errorMessage = 'Please enter a title for your post.';
      return false;
    }

    if (this.newPost.title.trim().length < 5) {
      this.errorMessage = 'Title must be at least 5 characters long.';
      return false;
    }

    if (this.newPost.title.trim().length > 200) {
      this.errorMessage = 'Title must be less than 200 characters.';
      return false;
    }

    if (!this.newPost.label || this.newPost.label.trim() === '') {
      this.errorMessage = 'Please select a community for your post.';
      return false;
    }

    if (!this.newPost.content || this.newPost.content.trim() === '') {
      this.errorMessage = 'Please enter content for your post.';
      return false;
    }

    // Check if content is just HTML tags without actual text
    const textContent = this.newPost.content.replace(/<[^>]*>/g, '').trim();
    if (textContent === '') {
      this.errorMessage = 'Please enter actual content for your post.';
      return false;
    }

    return true;
  }
}
