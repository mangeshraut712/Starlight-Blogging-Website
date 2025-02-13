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

    this.postService.getPostsByLabel(this.label).subscribe(
      (response: Post[]) => {
        this.posts = response.map(post => ({
          ...post,
          created_at: this.datePipe.transform(post.created_at, 'MM/dd/yyyy')
        }));
      },
      (error) => {
        console.log("error retrieving posts: ", error);
      }
    )
  }

  fetchPosts() {
    // fetch posts with the current label from the backend API
    this.postService.getPostsByLabel(this.label).subscribe(
      posts => {this.posts = posts;}
    );
  }

}
