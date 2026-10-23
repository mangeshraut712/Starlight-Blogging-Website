import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MatDialogModule } from '@angular/material/dialog';

import { PostCartComponent } from './post-cart.component';

describe('PostCartComponent', () => {
  let component: PostCartComponent;
  let fixture: ComponentFixture<PostCartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, FormsModule, MatDialogModule],
      declarations: [ PostCartComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PostCartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
