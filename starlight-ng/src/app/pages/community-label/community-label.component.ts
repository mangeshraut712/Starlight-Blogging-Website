import { DatePipe } from '@angular/common';
import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Post } from 'src/app/models/post';
import { PostService } from 'src/app/services/post.service';

@Component({
  selector: 'app-community-label',
  templateUrl: './community-label.component.html',
  styleUrls: ['./community-label.component.css']
})
export class CommunityLabelComponent {
  label: string;
  posts: Post[];

  isLoading = false;

  constructor(
    private route: ActivatedRoute, 
    private postService:PostService,
    private datePipe: DatePipe
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.label = params['label'];
      this.fetchPosts();
    });
  }

  fetchPosts() {
    this.isLoading = true;
    this.postService.getPostsByLabel(this.label).subscribe(
      posts => {
        this.posts = posts;
        this.isLoading = false;
      },
      error => {
        console.log("error retrieving posts: ", error);
        this.isLoading = false;
      }
    );
  }

}
