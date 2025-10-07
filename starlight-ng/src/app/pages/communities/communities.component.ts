import { Component } from '@angular/core';
import { DataService } from 'src/app/services/data.service';

@Component({
  selector: 'app-communities',
  templateUrl: './communities.component.html',
  styleUrls: ['./communities.component.css']
})
export class CommunitiesComponent {
  communityList: string[];

  constructor(private dataService: DataService) {
    this.communityList = this.dataService.communityList;
  }
}
