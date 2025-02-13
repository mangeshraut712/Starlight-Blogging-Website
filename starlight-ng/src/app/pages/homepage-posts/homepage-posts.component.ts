import { Component } from '@angular/core';
import { Post } from 'src/app/models/post';
import { PostService } from 'src/app/services/post.service';


@Component({
  selector: 'app-homepage-posts',
  templateUrl: './homepage-posts.component.html',
  styleUrls: ['./homepage-posts.component.css']
})
export class HomepagePostsComponent {


  public postList?: Post[];
  posts:Post[];

  constructor(
    private postService:PostService, 
  ){ 
  }

  ngOnInit(){

    this.postService.getUserPosts().subscribe(
      (response: Post[]) => {
        this.posts = response;
      },
      (error) => {
        console.log("error retrieving posts: ", error);
      }
    )
  }


}
