import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { User } from '../models/user';
import { Post } from '../models/post';
import { getApiBaseUrl } from '../utils/api-url';

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type': 'application/json',
    'Accept':'application/json'
  }),
  withCredentials: true
};

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private BASE_URL: string = getApiBaseUrl();

  constructor(private http: HttpClient) {}

  getAllUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.BASE_URL}/api/users`, httpOptions);
  }

  getUserById(id: number): Observable<User> {
    return this.http.get<User>(`${this.BASE_URL}/api/users/${id}`);
  }

  getAuthor(username: string): Observable<User> {
    return this.http.get<User>(`${this.BASE_URL}/api/authors/${username}`);
  }

  getAuthorPosts(username: string, page = 1): Observable<{posts: Post[]; page: number; per_page: number; total: number; has_more: boolean}> {
    return this.http.get<{posts: Post[]; page: number; per_page: number; total: number; has_more: boolean}>(
      `${this.BASE_URL}/api/authors/${username}/posts?page=${page}`
    );
  }

  followUser(userId: number, follow: boolean) {
    const method = follow ? 'post' : 'delete';
    return this.http.request(method, `${this.BASE_URL}/api/users/${userId}/follow`, httpOptions);
  }

  getUserData(): Observable<User> {
    return this.http.get<User>(`${this.BASE_URL}/api/current_user`, httpOptions);
  }

  updateUser(user: User): Observable<User> {
    return this.http.put<User>(`${this.BASE_URL}/api/update-profile`, user, httpOptions);
  }
}
