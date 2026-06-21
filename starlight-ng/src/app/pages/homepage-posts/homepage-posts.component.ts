import { Component } from '@angular/core';
import { Post } from 'src/app/models/post';
import { PostService } from 'src/app/services/post.service';
import { AuthService } from 'src/app/services/auth.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-homepage-posts',
  templateUrl: './homepage-posts.component.html',
  styleUrls: ['./homepage-posts.component.css']
})
export class HomepagePostsComponent {
  posts: Post[] = [];
  isLoading = false;
  isLoadingMore = false;
  sortOption = 'newest';
  isMyPostsRoute = false;
  page = 1;
  hasMore = false;
  total = 0;

  constructor(
    private postService: PostService,
    private authService: AuthService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.route.data.subscribe(data => {
      this.isMyPostsRoute = data['onlyUserPosts'] === true;
    });
    this.loadPosts(true);
  }

  loadPosts(reset = false): void {
    if (reset) {
      this.page = 1;
      this.posts = [];
    }
    this.isLoading = reset;
    this.isLoadingMore = !reset;

    if (this.isMyPostsRoute) {
      this.postService.getUserPosts().subscribe({
        next: (response) => {
          this.posts = this.sortPosts(response);
          this.hasMore = false;
          this.isLoading = false;
          this.isLoadingMore = false;
        },
        error: () => { this.isLoading = false; this.isLoadingMore = false; }
      });
      return;
    }

    this.postService.getPostsPaginated(this.page, 12, this.sortOption).subscribe({
      next: (response) => {
        this.posts = reset ? response.posts : [...this.posts, ...response.posts];
        this.hasMore = response.has_more;
        this.total = response.total;
        this.isLoading = false;
        this.isLoadingMore = false;
      },
      error: () => { this.isLoading = false; this.isLoadingMore = false; }
    });
  }

  loadMore(): void {
    if (!this.hasMore || this.isLoadingMore) return;
    this.page++;
    this.loadPosts(false);
  }

  sortPosts(posts: Post[]): Post[] {
    const sorted = [...posts];
    switch (this.sortOption) {
      case 'newest': return sorted.sort((a, b) => new Date(b.created_at!).getTime() - new Date(a.created_at!).getTime());
      case 'oldest': return sorted.sort((a, b) => new Date(a.created_at!).getTime() - new Date(b.created_at!).getTime());
      case 'most_liked': return sorted.sort((a, b) => (b.likes || 0) - (a.likes || 0));
      case 'least_liked': return sorted.sort((a, b) => (a.likes || 0) - (b.likes || 0));
      case 'alphabetical': return sorted.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
      default: return sorted;
    }
  }

  onSortChange(): void {
    this.loadPosts(true);
  }

  onPostDeleted(postId: number): void {
    this.posts = this.posts.filter(p => p.id !== postId);
  }

  trackByPost(index: number, post: Post): number {
    return post.id!;
  }
}
