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
    "Adventure",
    "Technology",
    "Science",
    "Business",
    "Sports",
    "Music",
    "Art",
    "Travel",
    "Food",
    "Health"
  ];

}
