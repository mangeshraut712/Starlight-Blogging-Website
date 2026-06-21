import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Post } from 'src/app/models/post';
import { PostService } from 'src/app/services/post.service';
import { DataService } from 'src/app/services/data.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {
  query = '';
  labelFilter = '';
  communityList: string[] = [];
  results: Post[] = [];
  isLoading = false;
  hasSearched = false;
  resultCount = 0;

  constructor(
    private postService: PostService,
    private dataService: DataService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.communityList = this.dataService.communityList;
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.query = params['q'] || '';
      this.labelFilter = params['label'] || '';
      if (this.query || this.labelFilter) {
        this.search();
      }
    });
  }

  search(): void {
    if (!this.query.trim() && !this.labelFilter) {
      return;
    }

    this.isLoading = true;
    this.hasSearched = true;

    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        q: this.query.trim() || null,
        label: this.labelFilter || null
      },
      queryParamsHandling: 'merge',
      replaceUrl: true
    });

    this.postService.searchPosts(this.query.trim(), this.labelFilter).subscribe({
      next: (response) => {
        this.results = response.results;
        this.resultCount = response.count;
        this.isLoading = false;
      },
      error: () => {
        this.results = [];
        this.resultCount = 0;
        this.isLoading = false;
      }
    });
  }

  clearSearch(): void {
    this.query = '';
    this.labelFilter = '';
    this.results = [];
    this.resultCount = 0;
    this.hasSearched = false;
    this.router.navigate(['/search']);
  }

  trackByPost(index: number, post: Post): number {
    return post.id;
  }
}
