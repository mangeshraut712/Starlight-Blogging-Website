import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Post, PaginatedPosts } from '../models/post';
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

@Injectable({ providedIn: 'root' })
export class PostService {
  private BASE_URL: string = environment.apiUrl || 'http://localhost:8080';

  constructor(private http: HttpClient) {}

  getAllPosts(): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.BASE_URL}/api/posts`);
  }

  getPostsPaginated(page = 1, perPage = 12, sort = 'newest', label?: string): Observable<PaginatedPosts> {
    let url = `${this.BASE_URL}/api/posts?page=${page}&per_page=${perPage}&sort=${sort}`;
    if (label) url += `&label=${encodeURIComponent(label)}`;
    return this.http.get<PaginatedPosts>(url);
  }

  getTrending(limit = 6): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.BASE_URL}/api/trending?limit=${limit}`);
  }

  getPlatformStats(): Observable<{writers: number; posts: number; communities: number; comments: number; total_likes: number}> {
    return this.http.get<{writers: number; posts: number; communities: number; comments: number; total_likes: number}>(`${this.BASE_URL}/api/stats`);
  }

  getPostsByLabel(label: string): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.BASE_URL}/api/posts?label=${encodeURIComponent(label)}`);
  }

  getUserPosts(): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.BASE_URL}/api/user-posts`, httpOptions);
  }

  getPost(id: number): Observable<Post> {
    return this.http.get<Post>(`${this.BASE_URL}/api/posts/${id}`);
  }

  getPostBySlug(slug: string): Observable<Post> {
    return this.http.get<Post>(`${this.BASE_URL}/api/posts/slug/${slug}`);
  }

  addPost(post: Post): Observable<Post> {
    return this.http.post<Post>(`${this.BASE_URL}/api/new-post`, post, httpOptions);
  }

  deletePost(postId: number): Observable<unknown> {
    return this.http.delete(`${this.BASE_URL}/api/delete-post/${postId}`, httpOptions);
  }

  updatePost(postId: number, postData: {title: string; content: string}): Observable<Post> {
    return this.http.put<Post>(`${this.BASE_URL}/api/update-post/${postId}`, postData, httpOptions);
  }

  likePost(postId: number) {
    return this.http.post(`${this.BASE_URL}/api/posts/${postId}/like`, {}, httpOptions);
  }

  getPostLikes(postId: number): Observable<Like[]> {
    return this.http.get<Like[]>(`${this.BASE_URL}/api/posts/${postId}/likes`);
  }

  commentPost(postId: number, body: string) {
    return this.http.post(`${this.BASE_URL}/api/posts/${postId}/comments`, { body }, httpOptions);
  }

  getPostComments(postId: number): Observable<Comment[]> {
    return this.http.get<Comment[]>(`${this.BASE_URL}/api/posts/${postId}/comments`);
  }

  deleteComment(commentId: number) {
    return this.http.delete(`${this.BASE_URL}/api/delete-comment/${commentId}`, httpOptions);
  }

  updateComment(commentId: number, body: string) {
    return this.http.put(`${this.BASE_URL}/api/update-comment/${commentId}`, { body }, httpOptions);
  }

  searchPosts(query: string, label?: string): Observable<{results: Post[]; count: number; query: string; label: string}> {
    let url = `${this.BASE_URL}/api/search?`;
    const params: string[] = [];
    if (query) params.push(`q=${encodeURIComponent(query)}`);
    if (label) params.push(`label=${encodeURIComponent(label)}`);
    url += params.join('&');
    return this.http.get<{results: Post[]; count: number; query: string; label: string}>(url);
  }

  toggleBookmark(postId: number, bookmark: boolean) {
    const method = bookmark ? 'post' : 'delete';
    return this.http.request(method, `${this.BASE_URL}/api/posts/${postId}/bookmark`, httpOptions);
  }

  getBookmarks(): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.BASE_URL}/api/bookmarks`, httpOptions);
  }
}
