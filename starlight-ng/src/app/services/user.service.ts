import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { User } from '../models/user';

const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json' })
};

@Injectable({
  providedIn: 'root'
})
export class UserService {
   private BASE_URL: string = 'http://localhost:8080';
  private apiUrl = 'http://localhost:5000/api/users';
  private updateUrl = 'http://localhost:5000/api/update-profile';
  
  
  constructor(private http: HttpClient) { }

   /** GET users from the server */
   getAllUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.BASE_URL}/api/users`);
  }
  
  /** GET user by id. Will 404 if id not found */
  getUserById(id: number): Observable<User> {
    const url = `${this.BASE_URL}/api/users/${id}`;
    // return this.http.get<User>(url);
    return this.http.get<User>(url);
  }
  

  getUserData(): Observable<User> {
    // Pass the session ID in the withCredentials option
    return this.http.get<User>(`${this.BASE_URL}/api/current_user`, { withCredentials: true });
    // { withCredentials: true }
  }
  /** PUT: update the user on the server */
  updateUser(user: User): Observable<User> {
    // const url = `${this.apiUrl}/${user.id}`
    // return this.http.put(this.userUrl + '/update', user, httpOptions);
    // return this.http.put<User>(url, user, httpOptions);
    return this.http.put<User>(`${this.BASE_URL}/api/update-profile`, user, httpOptions);
  
  }
}