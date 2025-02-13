import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';


const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json',Accept:'application/json' })
};

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // private apiBaseUrl = 'http://localhost:5000';
  private BASE_URL: string = 'http://localhost:8080';

  private uid="uid";
  private registerUrl = 'http://localhost:5000/api/register';
  private logoutUrl = 'http://localhost:5000/api/logout';
  private dataUrl = 'http://localhost:5000/api/data';

  private loggedIn  = false;
  private tokenKey = 'my-auth-token';

  constructor(private http: HttpClient) {
    this.loggedIn  = !!localStorage.getItem('access_token');
  }
  setUid(uid: string): void {
    
    localStorage.setItem(this.uid, uid);
  }
  getUid(){
    return localStorage.getItem(this.uid);
  }

  test(): string {
    return 'working';
  }

  isLoggedIn(): boolean {
    // return this.loggedIn;
    const token = localStorage.getItem(this.tokenKey); // Get token from local storage
    return token != null;
  }

  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  login(email: string, password: string): Observable<any> {
    let url: string = `${this.BASE_URL}/api/login`; //`${this.apiBaseUrl}/register`
    // return this.http.post<any>(url, {email, password}, httpOptions);
    const options = { withCredentials: true};
    return this.http.post<any>(`${this.BASE_URL}/api/login`, {email, password}, httpOptions);
  }

  register(email: string, first:string, last:string, password: string): Observable<any> {
    let url: string = `${this.BASE_URL}/register`; //`${this.apiBaseUrl}/register`
    // const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.post<any>(`${this.BASE_URL}/api/register`, { email, first, last, password }, httpOptions);
  }

  forgotPassword(email: string): Observable<any> {
    // const url = `${this.BASE_URL}/forgot_password`;
    // return this.http.post(url, { email });
    return this.http.post<any>(`${this.BASE_URL}/api/forgot_password`, { email });
  }

  resetPassword(userId:number, newPassword:string, confirmPassword:string): Observable<any> {
    // const url = `${this.BASE_URL}/forgot_password`;
    // return this.http.post(url, { email });
    const body = {
      user_id: userId,
      new_password: newPassword,
      confirm_password: confirmPassword
    };
    return this.http.post<any>(`${this.BASE_URL}/api/reset_password`, body);
  }

  logout(): Observable<any> {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.uid);
    return this.http.get<any>(`${this.BASE_URL}/api/logout`);
  }

  getData(): Observable<any> {
    return this.http.get<any>(`${this.BASE_URL}/api/data`);
  }
}