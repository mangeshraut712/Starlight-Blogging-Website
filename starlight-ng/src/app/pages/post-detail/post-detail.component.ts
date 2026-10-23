import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SecurityContext } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { Post } from 'src/app/models/post';
import { Comment } from 'src/app/models/comment';
import { PostService } from 'src/app/services/post.service';
import { UserService } from 'src/app/services/user.service';
import { AuthService } from 'src/app/services/auth.service';
import { MetaService } from 'src/app/services/meta.service';

function stripTags(value: string): string {
  let out = "";
  let inTag = false;
  for (const ch of value) {
    if (ch === "<") inTag = true;
    else if (ch === ">") inTag = false;
    else if (!inTag) out += ch;
  }
  return out;
}


@Component({
  selector: 'app-post-detail',
  standalone: false,
  templateUrl: './post-detail.component.html',
  styleUrls: ['./post-detail.component.css']
})
export class PostDetailComponent implements OnInit, OnDestroy {
  post: Post = new Post();
  comments: Comment[] = [];
  newComment = '';
  isLoading = true;
  isLiked = false;
  isBookmarked = false;
  isFollowing = false;
  errorMessage = '';
  readingProgress = 0;
  safeContent = '';
  shareCopied = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private postService: PostService,
    private userService: UserService,
    public authService: AuthService,
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
        const sanitized = this.sanitizer.sanitize(SecurityContext.HTML, post.content || '') || '';
        this.safeContent = sanitized;
        this.isBookmarked = !!post.is_bookmarked;
        this.isFollowing = !!post.is_following_author;
        this.isLiked = !!post.is_liked;
        this.metaService.setPageMeta({
          title: post.title || 'Story',
          description: post.excerpt || '',
          author: post.author_name
        });
        this.loadComments();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'This story could not be found.';
        this.isLoading = false;
      }
    });
  }

  loadComments(): void {
    if (!this.post.id) return;
    this.postService.getPostComments(this.post.id).subscribe({
      next: (comments) => this.comments = comments
    });
  }

  getReadingTime(): number {
    if (this.post.reading_minutes) {
      return this.post.reading_minutes;
    }
    const text = stripTags(this.post.content || '');
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

  toggleBookmark(): void {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    if (!this.post.id) return;
    const next = !this.isBookmarked;
    this.postService.toggleBookmark(this.post.id, next).subscribe({
      next: () => this.isBookmarked = next
    });
  }

  toggleFollow(): void {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    if (!this.post.author_id || this.post.author_id === Number(this.authService.getUid())) return;
    const next = !this.isFollowing;
    this.userService.followUser(this.post.author_id, next).subscribe({
      next: () => this.isFollowing = next
    });
  }

  goToAuthor(): void {
    if (this.post.author_username) {
      this.router.navigate(['/author', this.post.author_username]);
    }
  }

  isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }
}
