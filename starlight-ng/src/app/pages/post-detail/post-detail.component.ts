import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { Post } from 'src/app/models/post';
import { Comment } from 'src/app/models/comment';
import { User } from 'src/app/models/user';
import { PostService } from 'src/app/services/post.service';
import { UserService } from 'src/app/services/user.service';
import { AuthService } from 'src/app/services/auth.service';
import { MetaService } from 'src/app/services/meta.service';

@Component({
  selector: 'app-post-detail',
  templateUrl: './post-detail.component.html',
  styleUrls: ['./post-detail.component.css']
})
export class PostDetailComponent implements OnInit, OnDestroy {
  post: Post = new Post();
  author?: User;
  comments: Comment[] = [];
  newComment = '';
  isLoading = true;
  isLiked = false;
  isBookmarked = false;
  isFollowing = false;
  errorMessage = '';
  readingProgress = 0;
  safeContent: SafeHtml = '';
  shareCopied = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private postService: PostService,
    private userService: UserService,
    private authService: AuthService,
    private metaService: MetaService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    window.addEventListener('scroll', this.onScroll);
    this.route.params.subscribe(params => {
      const slug = params['slug'];
      if (slug) this.loadPost(slug);
    });
  }

  ngOnDestroy(): void {
    window.removeEventListener('scroll', this.onScroll);
    this.metaService.resetMeta();
  }

  onScroll = (): void => {
    const doc = document.documentElement;
    const scrollTop = doc.scrollTop || document.body.scrollTop;
    const scrollHeight = doc.scrollHeight - doc.clientHeight;
    this.readingProgress = scrollHeight > 0 ? Math.min(100, (scrollTop / scrollHeight) * 100) : 0;
  };

  loadPost(slug: string): void {
    this.isLoading = true;
    this.postService.getPostBySlug(slug).subscribe({
      next: (post) => {
        this.post = post;
        this.safeContent = this.sanitizer.bypassSecurityTrustHtml(post.content || '');
        this.metaService.setPageMeta({
          title: post.title || 'Story',
          description: post.excerpt || '',
          author: post.author_name
        });
        this.loadAuthor();
        this.loadComments();
        if (this.authService.isLoggedIn()) {
          this.checkLikeStatus();
        }
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'This story could not be found.';
        this.isLoading = false;
      }
    });
  }

  loadAuthor(): void {
    if (!this.post.author_id) return;
    this.userService.getUserById(this.post.author_id).subscribe({
      next: (user) => this.author = user
    });
  }

  loadComments(): void {
    if (!this.post.id) return;
    this.postService.getPostComments(this.post.id).subscribe({
      next: (comments) => this.comments = comments
    });
  }

  checkLikeStatus(): void {
    if (!this.post.id) return;
    const uid = Number(this.authService.getUid());
    this.postService.getPostLikes(this.post.id).subscribe({
      next: (likes) => this.isLiked = likes.some(l => l.user_id === uid)
    });
  }

  getReadingTime(): number {
    const text = (this.post.content || '').replace(/<[^>]*>/g, '');
    const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
    return Math.max(1, Math.ceil(words / 200));
  }

  toggleLike(): void {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    if (!this.post.id) return;
    this.postService.likePost(this.post.id).subscribe({
      next: () => {
        this.isLiked = !this.isLiked;
        this.post.likes = (this.post.likes || 0) + (this.isLiked ? 1 : -1);
      }
    });
  }

  submitComment(): void {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    if (!this.newComment.trim() || !this.post.id) return;
    this.postService.commentPost(this.post.id, this.newComment.trim()).subscribe({
      next: (comment: any) => {
        this.comments.unshift(comment);
        this.newComment = '';
      }
    });
  }

  sharePost(): void {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      this.shareCopied = true;
      setTimeout(() => this.shareCopied = false, 2000);
    });
  }

  goToAuthor(): void {
    if (this.author?.username) {
      this.router.navigate(['/author', this.author.username]);
    }
  }

  isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }
}
