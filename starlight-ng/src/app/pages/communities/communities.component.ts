import { Component } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { PostService } from 'src/app/services/post.service';
import { Post } from 'src/app/models/post';

interface CommunityWithStats {
  name: string;
  postCount: number;
  latestPostDate: Date | null;
}

@Component({
  selector: 'app-communities',
  templateUrl: './communities.component.html',
  styleUrls: ['./communities.component.css']
})
export class CommunitiesComponent {
  communities: CommunityWithStats[] = [];
  sortOption: string = 'alphabetical';
  filterOption: string = 'all';
  isLoading: boolean = true;

  constructor(
    private dataService: DataService,
    private postService: PostService
  ) {
    this.loadCommunities();
  }

  loadCommunities() {
    this.isLoading = true;
    this.postService.getAllPosts().subscribe(
      (posts: Post[]) => {
        // Count posts per community and get latest dates
        const communityStats = new Map<string, CommunityWithStats>();

        // Initialize all communities
        this.dataService.communityList.forEach(community => {
          communityStats.set(community, {
            name: community,
            postCount: 0,
            latestPostDate: null
          });
        });

        // Update with actual post data
        posts.forEach(post => {
          if (communityStats.has(post.label)) {
            const stats = communityStats.get(post.label)!;
            stats.postCount++;
            const postDate = new Date(post.created_at);
            if (!stats.latestPostDate || postDate > stats.latestPostDate) {
              stats.latestPostDate = postDate;
            }
          }
        });

        this.communities = Array.from(communityStats.values());
        this.sortCommunities();
        this.isLoading = false;
      },
      (error) => {
        console.error('Error loading posts for communities:', error);
        // Fallback to basic list
        this.communities = this.dataService.communityList.map(name => ({
          name,
          postCount: 0,
          latestPostDate: null
        }));
        this.sortCommunities();
        this.isLoading = false;
      }
    );
  }

  sortCommunities() {
    switch (this.sortOption) {
      case 'alphabetical':
        this.communities.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'newest':
        this.communities.sort((a, b) => {
          if (!a.latestPostDate && !b.latestPostDate) return 0;
          if (!a.latestPostDate) return 1;
          if (!b.latestPostDate) return -1;
          return b.latestPostDate.getTime() - a.latestPostDate.getTime();
        });
        break;
      case 'oldest':
        this.communities.sort((a, b) => {
          if (!a.latestPostDate && !b.latestPostDate) return 0;
          if (!a.latestPostDate) return 1;
          if (!b.latestPostDate) return -1;
          return a.latestPostDate.getTime() - b.latestPostDate.getTime();
        });
        break;
      case 'most_posts':
        this.communities.sort((a, b) => b.postCount - a.postCount);
        break;
      case 'least_posts':
        this.communities.sort((a, b) => a.postCount - b.postCount);
        break;
    }
  }

  getFilteredCommunities(): CommunityWithStats[] {
    switch (this.filterOption) {
      case 'with_posts':
        return this.communities.filter(c => c.postCount > 0);
      case 'without_posts':
        return this.communities.filter(c => c.postCount === 0);
      case 'most_active':
        return this.communities.filter(c => c.postCount >= 5);
      default: // 'all'
        return this.communities;
    }
  }

  onSortChange() {
    this.sortCommunities();
  }

  onFilterChange() {
    // No additional sorting needed, just filtering
  }
}
