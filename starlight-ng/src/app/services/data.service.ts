import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class DataService {
 
  communityList:string[]=[
    "Fantasy",
    "Essay",
    "Comedy",
    "Fiction",
    "Horror",
    "Romance",
    "Adventure"
  ];

}
