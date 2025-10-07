import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';

import { Post } from '../models/post';
import { Like } from '../models/like';
import { Comment } from '../models/comment';
import { environment } from '../../environments/environment';

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }),
  withCredentials: true
};

@Injectable({
  providedIn: 'root'
})
export class PostService {
   private BASE_URL: string = environment.apiUrl || 'http://localhost:8080';

  constructor(private http: HttpClient) { }

  getAllPosts(): Observable<Post[]> {
    // return this.http.get<Post[]>(this.postsApiUrl);
    return this.http.get<Post[]>(`${this.BASE_URL}/api/posts`);
  }

  getPostsByLabel(label:string): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.BASE_URL}/api/posts?label=${label}`);
  }

  getUserPosts(): Observable<Post[]> {
    // return this.http.get<Post[]>(this.postsApiUrl);
    return this.http.get<Post[]>(`${this.BASE_URL}/api/user-posts`);
  }

  getPost(id: number) {
    return this.http.get(`${this.BASE_URL}/api/posts/${id}`);
  }

  // makeNewPost(title:string, content:string, label:string, likes:number, author_id:number): Observable<Post> {
  addPost(post:Post): Observable<Post> {
    return this.http.post<Post>(`${this.BASE_URL}/api/new-post`, post, httpOptions);
    // return this.http.post<Post>(this.newpostUrl, post);
    // return this.http.post<Post>(this.newpostUrl, {title, content, label, likes, author_id});
  }

  deletePost(postId:number): Observable<Post>{
    const url = `${this.BASE_URL}/api/delete-post/${postId}`;
    return this.http.delete<Post>(url);
  }

  likePost(postId:number) {
    // const body = { action: action };
    // return this.http.post(`${this.postsApiUrl}/${postId}/like`, body);
    return this.http.post(`${this.BASE_URL}/api/posts/${postId}/like`, {}, httpOptions);
  }

  getPostLikes(postId:number): Observable<Like[]> {
    return this.http.get<Like[]>(`${this.BASE_URL}/api/posts/${postId}/likes`);
  }

  commentPost(postId:number, body:string) {
    // const body = { action: action };
    // return this.http.post(`${this.postsApiUrl}/${postId}/comment`, body);
    return this.http.post(`${this.BASE_URL}/api/posts/${postId}/comments`, {body}, httpOptions);
  }

  getPostComments(postId:number): Observable<Comment[]> {
    return this.http.get<Comment[]>(`${this.BASE_URL}/api/posts/${postId}/comments`);
  }

  deleteComment(commentId: number) {
    return this.http.delete(`${this.BASE_URL}/api/delete-comment/${commentId}`, httpOptions);
  }

  updateComment(commentId: number, body: string) {
    return this.http.put(`${this.BASE_URL}/api/update-comment/${commentId}`, { body }, httpOptions);
  }
}
