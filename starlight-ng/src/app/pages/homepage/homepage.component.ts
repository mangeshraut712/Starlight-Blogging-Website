import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Post } from 'src/app/models/post';
import { PostService } from 'src/app/services/post.service';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-homepage',
  templateUrl: './homepage.component.html',
  styleUrls: ['./homepage.component.css']
})
export class HomepageComponent implements OnInit {
  trendingPosts: Post[] = [];
  stats = { writers: 0, posts: 0, communities: 0, comments: 0 };
  isLoading = true;

  constructor(
    private router: Router,
    private postService: PostService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    this.postService.getTrending(6).subscribe({
      next: (posts) => { this.trendingPosts = posts; },
      error: () => {}
    });
    this.postService.getPlatformStats().subscribe({
      next: (stats) => { this.stats = stats; this.isLoading = false; },
      error: () => { this.isLoading = false; }
    });
  }

  startWriting(): void {
    this.router.navigate([this.authService.isLoggedIn() ? '/new-post' : '/registration']);
  }

  exploreStories(): void {
    this.router.navigate(['/explore']);
  }
}
