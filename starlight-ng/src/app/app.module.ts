import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ToastModule } from '@coreui/angular';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { EditorModule } from '@tinymce/tinymce-angular';
import { FormsModule } from '@angular/forms';
import { MatDialogModule } from '@angular/material/dialog';
import { HttpClientModule } from '@angular/common/http'; 
import { DatePipe } from '@angular/common';


import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './pages/login/login.component';
import { HomepageComponent } from './pages/homepage/homepage.component';
import { NavbarComponent } from './components/navbar/navbar.component';
import { RegistrationComponent } from './pages/registration/registration.component';
import { RecoveryComponent } from './pages/recovery/recovery.component';
import { ChangePasswordComponent } from './pages/change-password/change-password.component';
import { HomepagePostsComponent } from './pages/homepage-posts/homepage-posts.component';
import { PostCartComponent } from './components/post-cart/post-cart.component';
import { NewPostComponent } from './pages/new-post/new-post.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { UpdateProfileComponent } from './pages/update-profile/update-profile.component';
import { PopUpComponent } from './components/pop-up/pop-up.component';
import { CommunityLabelComponent } from './pages/community-label/community-label.component';

// SERVICES
import { AuthService } from './services/auth.service';
import { UserService } from './services/user.service';
import { PostService } from './services/post.service';
import { DataService } from './services/data.service';


@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    HomepageComponent,
    NavbarComponent,
    RegistrationComponent,
    RecoveryComponent,
    ChangePasswordComponent,
    HomepagePostsComponent,
    PostCartComponent,
    NewPostComponent,
    UpdateProfileComponent,
    PopUpComponent,
    CommunityLabelComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ToastModule,
    BrowserAnimationsModule,
    MatSnackBarModule,
    EditorModule,
    FormsModule,
    MatDialogModule,
    HttpClientModule
  ],
  providers: [
    AuthService, 
    DatePipe,
    UserService,
    PostService,
    DataService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
