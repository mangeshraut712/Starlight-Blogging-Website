import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { PopUpComponent } from '../pop-up/pop-up.component';
import { Router } from '@angular/router';
import { Post } from 'src/app/models/post';
import { User } from 'src/app/models/user';
import { Comment } from 'src/app/models/comment';
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
  @Output() postDeleted = new EventEmitter<number>();

  isLiked = false;
  seeComments = false;
  user: User;
  comments: Comment[] = [];
  newComment: Comment;
  successMessage = '';
  editingCommentId: number | null = null;
  editingCommentText = '';

  constructor(
    private dialogRef: MatDialog,
    private userService: UserService,
    private postService: PostService,
    private router: Router,
    public authService: AuthService
  ) {
    this.user = new User();
    this.comments = [];
    this.newComment = new Comment();
    this.currentPost = new Post();
  }

  ngOnInit(): void {
    if (this.authService.isLoggedIn()) {
      this.getUser();
    }
    if (this.currentPost?.id) {
      this.getPostLikes();
      this.getPostComments();
    }
  }

  get postLink(): string[] {
    return this.currentPost.slug ? ['/post', this.currentPost.slug] : ['/post', String(this.currentPost.id)];
  }

  get authorLink(): string[] | null {
    const username = this.currentPost.author_username;
    return username ? ['/author', username] : null;
  }

  getUser(): void {
    const uid = Number(this.authService.getUid());
    if (!uid) return;
    this.userService.getUserById(uid).subscribe(data => this.user = data);
  }

  getPostLikes(): void {
    this.postService.getPostLikes(this.currentPost.id!).subscribe(likes => {
      this.isLiked = likes.some(like => like.user_id === this.user?.id);
    });
  }

  getPostComments(): void {
    this.postService.getPostComments(this.currentPost.id!).subscribe(comments => {
      this.comments = comments;
    });
  }

  getExcerpt(): string {
    if (this.currentPost.excerpt) return this.currentPost.excerpt;
    const text = (this.currentPost.content || '').replace(/<[^>]*>/g, '');
    return text.length > 180 ? text.slice(0, 180) + '...' : text;
  }

  deletePost(post: Post): void {
    const dialog = this.dialogRef.open(PopUpComponent, {
      data: { message: 'Are you sure you want to delete this post?' }
    });
    dialog.afterClosed().subscribe(result => {
      if (result && post.id) {
        this.postService.deletePost(post.id).subscribe({
          next: () => this.postDeleted.emit(post.id),
          error: (err) => console.error('Delete failed', err)
        });
      }
    });
  }

  isOwnPost(): boolean {
    return !!this.user?.id && this.user.id === this.currentPost.author_id;
  }

  editPost(): void {
    this.router.navigate(['/edit-post', this.currentPost.id]);
  }

  showComments(): void {
    this.seeComments = !this.seeComments;
  }

  submitComment(): void {
    if (!this.newComment.body?.trim() || !this.currentPost.id) return;
    this.postService.commentPost(this.currentPost.id, this.newComment.body.trim()).subscribe({
      next: (comment: Comment) => {
        this.comments.unshift(comment);
        this.newComment.body = '';
      }
    });
  }

  toggleLike(): void {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    this.postService.likePost(this.currentPost.id!).subscribe({
      next: () => {
        this.isLiked = !this.isLiked;
        this.currentPost.likes = (this.currentPost.likes || 0) + (this.isLiked ? 1 : -1);
      }
    });
  }

  sharePost(): void {
    const slug = this.currentPost.slug || this.currentPost.id;
    const url = `${window.location.origin}/post/${slug}`;
    navigator.clipboard.writeText(url);
    this.successMessage = 'Link copied!';
    setTimeout(() => this.successMessage = '', 2000);
  }

  editComment(comment: Comment): void {
    this.editingCommentId = comment.id!;
    this.editingCommentText = comment.body;
  }

  cancelEdit(): void {
    this.editingCommentId = null;
    this.editingCommentText = '';
  }

  saveCommentEdit(comment: Comment): void {
    if (!this.editingCommentText.trim() || !comment.id) return;
    this.postService.updateComment(comment.id, this.editingCommentText.trim()).subscribe({
      next: (updated) => {
        const idx = this.comments.findIndex(c => c.id === comment.id);
        if (idx !== -1) this.comments[idx] = updated as Comment;
        this.cancelEdit();
      }
    });
  }

  deleteComment(comment: Comment): void {
    if (!comment.id || !confirm('Delete this comment?')) return;
    this.postService.deleteComment(comment.id).subscribe({
      next: () => this.comments = this.comments.filter(c => c.id !== comment.id)
    });
  }

  isOwnComment(comment: Comment): boolean {
    return !!this.user?.id && this.user.id === comment.author_id;
  }

  getReadingTime(): number {
    const text = (this.currentPost?.content || '').replace(/<[^>]*>/g, '');
    const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
    return Math.max(1, Math.ceil(words / 200));
  }
}
