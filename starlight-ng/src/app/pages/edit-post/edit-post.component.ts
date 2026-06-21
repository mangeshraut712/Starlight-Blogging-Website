import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Post } from 'src/app/models/post';
import { AuthService } from 'src/app/services/auth.service';
import { DataService } from 'src/app/services/data.service';
import { PostService } from 'src/app/services/post.service';

@Component({
  selector: 'app-edit-post',
  templateUrl: './edit-post.component.html',
  styleUrls: ['./edit-post.component.css']
})
export class EditPostComponent implements OnInit {
  communityList: string[] = [];
  post: Post = new Post();
  postId: number = 0;
  errorMessage = '';
  isLoading = false;
  isSaving = false;

  editorConfig = {
    base_url: '/tinymce',
    suffix: '.min',
    license_key: 'gpl',
    plugins: 'lists link table code help wordcount',
    toolbar: 'undo redo | blocks | bold italic | alignleft aligncenter alignright | bullist numlist outdent indent | link | code | help',
    menubar: false,
    branding: false,
    height: 400,
    content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; }'
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private data: DataService,
    private postService: PostService,
    private authService: AuthService
  ) {
    this.communityList = this.data.communityList;
  }

  ngOnInit(): void {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }

    this.route.params.subscribe(params => {
      this.postId = +params['id'];
      this.loadPost();
    });
  }

  loadPost(): void {
    this.isLoading = true;
    this.postService.getPost(this.postId).subscribe({
      next: (data: any) => {
        this.post = data;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Post not found or you do not have permission to edit it.';
        this.isLoading = false;
      }
    });
  }

  cancelEdit(): void {
    this.router.navigate(['/explore']);
  }

  savePost(): void {
    if (this.isSaving || !this.validateForm()) return;

    this.isSaving = true;
    this.errorMessage = '';

    const postData = {
      title: this.post.title?.trim() || '',
      content: this.post.content?.trim() || ''
    };

    this.postService.updatePost(this.postId, postData).subscribe({
      next: () => {
        this.isSaving = false;
        this.router.navigate(['/explore']);
      },
      error: (error) => {
        this.isSaving = false;
        if (error.status === 403) {
          this.errorMessage = 'You can only edit your own posts.';
        } else {
          this.errorMessage = 'Failed to update post. Please try again.';
        }
      }
    });
  }

  private validateForm(): boolean {
    if (!this.post.title?.trim()) {
      this.errorMessage = 'Please enter a title.';
      return false;
    }
    if (!this.post.content?.trim()) {
      this.errorMessage = 'Please enter content.';
      return false;
    }
    const textContent = this.post.content.replace(/<[^>]*>/g, '').trim();
    if (!textContent) {
      this.errorMessage = 'Please enter actual content.';
      return false;
    }
    return true;
  }
}
