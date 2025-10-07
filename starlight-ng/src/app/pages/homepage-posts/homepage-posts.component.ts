import { Component } from '@angular/core';
import { Post } from 'src/app/models/post';
import { PostService } from 'src/app/services/post.service';
import { AuthService } from 'src/app/services/auth.service';


@Component({
  selector: 'app-homepage-posts',
  templateUrl: './homepage-posts.component.html',
  styleUrls: ['./homepage-posts.component.css']
})
export class HomepagePostsComponent {
  public postList?: Post[];
  posts: Post[] = [];
  isLoading = false;
  sortOption = 'newest';
  filterOption = 'all';

  constructor(
    private postService: PostService,
    private authService: AuthService
  ) {}

  ngOnInit(){
    this.loadPosts();
  }

  loadPosts() {
    this.isLoading = true;
    const uid = Number(this.authService.getUid());
    if (uid) {
      // Show only current user's posts
      this.postService.getUserPosts().subscribe(
        (response: Post[]) => {
          this.posts = this.sortPosts(response);
          this.isLoading = false;
        },
        (error) => {
          console.log("error retrieving user posts: ", error);
          this.isLoading = false;
        }
      );
    } else {
      // Fallback - shouldn't happen since this is protected route
      this.posts = [];
      this.isLoading = false;
    }
  }

  sortPosts(posts: Post[]): Post[] {
    const sorted = [...posts];
    switch (this.sortOption) {
      case 'newest':
        return sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      case 'oldest':
        return sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      case 'most_liked':
        return sorted.sort((a, b) => (b.likes || 0) - (a.likes || 0));
      case 'least_liked':
        return sorted.sort((a, b) => (a.likes || 0) - (b.likes || 0));
      case 'longest':
        return sorted.sort((a, b) => (b.content?.length || 0) - (a.content?.length || 0));
      case 'shortest':
        return sorted.sort((a, b) => (a.content?.length || 0) - (b.content?.length || 0));
      case 'alphabetical':
        return sorted.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
      default:
        return sorted;
    }
  }

  onSortChange() {
    this.posts = this.sortPosts(this.posts);
  }

  onPostDeleted() {
    // Reload posts after deletion
    this.loadPosts();
  }
}
