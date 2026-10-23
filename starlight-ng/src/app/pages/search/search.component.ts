import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Post } from 'src/app/models/post';
import { PostService } from 'src/app/services/post.service';
import { DataService } from 'src/app/services/data.service';
import { MetaService } from 'src/app/services/meta.service';

@Component({
  selector: 'app-search',
  standalone: false,
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit, OnDestroy {
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
    private router: Router,
    private metaService: MetaService
  ) {
    this.communityList = this.dataService.communityList;
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.query = params['q'] || '';
      this.labelFilter = params['label'] || '';
      if (this.query || this.labelFilter) {
        this.runSearch();
      }
    });
  }

  ngOnDestroy(): void {
    this.metaService.resetMeta();
  }

  search(): void {
    if (!this.query.trim() && !this.labelFilter) {
      return;
    }

    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        q: this.query.trim() || null,
        label: this.labelFilter || null
      },
      queryParamsHandling: 'merge',
      replaceUrl: true
    });
  }

  private runSearch(): void {
    this.isLoading = true;
    this.hasSearched = true;
    this.metaService.setPageMeta({
      title: this.query ? `Search: ${this.query}` : 'Search',
      description: 'Find stories on StarLight',
      type: 'website'
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
