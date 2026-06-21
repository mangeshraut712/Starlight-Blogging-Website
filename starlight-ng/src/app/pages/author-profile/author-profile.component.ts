import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { User } from 'src/app/models/user';
import { Post } from 'src/app/models/post';
import { UserService } from 'src/app/services/user.service';
import { AuthService } from 'src/app/services/auth.service';
import { MetaService } from 'src/app/services/meta.service';

@Component({
  selector: 'app-author-profile',
  templateUrl: './author-profile.component.html',
  styleUrls: ['./author-profile.component.css']
})
export class AuthorProfileComponent implements OnInit {
  author?: User;
  posts: Post[] = [];
  username = '';
  isLoading = true;
  isFollowing = false;

  constructor(
    private route: ActivatedRoute,
    private userService: UserService,
    private authService: AuthService,
    private metaService: MetaService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.username = params['username'];
      this.loadAuthor();
    });
  }

  loadAuthor(): void {
    this.isLoading = true;
    this.userService.getAuthor(this.username).subscribe({
      next: (author) => {
        this.author = author;
        this.isFollowing = !!author.is_following;
        this.metaService.setPageMeta({
          title: `${author.first} ${author.last}`,
          description: author.bio || `Stories by ${author.first} ${author.last} on StarLight`
        });
        this.loadPosts();
      },
      error: () => { this.isLoading = false; }
    });
  }

  loadPosts(): void {
    this.userService.getAuthorPosts(this.username).subscribe({
      next: (res) => {
        this.posts = res.posts;
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  toggleFollow(): void {
    if (!this.authService.isLoggedIn() || !this.author?.id) return;
    this.userService.followUser(this.author.id, !this.isFollowing).subscribe({
      next: () => this.isFollowing = !this.isFollowing
    });
  }

  isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }
}
