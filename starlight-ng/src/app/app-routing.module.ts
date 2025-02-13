import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { LoginComponent } from './pages/login/login.component';
import { HomepageComponent } from './pages/homepage/homepage.component';
import { RegistrationComponent } from './pages/registration/registration.component';
import { RecoveryComponent } from './pages/recovery/recovery.component';
import { ChangePasswordComponent } from './pages/change-password/change-password.component';
import { HomepagePostsComponent } from './pages/homepage-posts/homepage-posts.component';
import { NewPostComponent } from './pages/new-post/new-post.component';
import { UpdateProfileComponent } from './pages/update-profile/update-profile.component';
import { CommunityLabelComponent } from './pages/community-label/community-label.component';

import { AuthGuard } from './services/auth.guard';

const routes: Routes = [
  {
    path: '',
    component: HomepageComponent,
  },
  {
    path: 'registration',
    component: RegistrationComponent,
  },
  {
    path: 'login',
    component: LoginComponent,
  },
  {
    path: 'recovery',
    component: RecoveryComponent,
  },
  {
    path: 'change-password/:user_id',
    component: ChangePasswordComponent,
  },
  {
    path:'homepage-posts',
    component: HomepagePostsComponent,
    canActivate: [AuthGuard]
  },
  {
    path:'new-post',
    component: NewPostComponent,
    canActivate: [AuthGuard]
  },
  {
    path:'community/:label',
    component: CommunityLabelComponent,
    canActivate: [AuthGuard]
  },
  {
    path:'update-profile',
    component: UpdateProfileComponent,
    canActivate: [AuthGuard]
  }

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
