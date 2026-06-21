import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { HomepageComponent } from './pages/homepage/homepage.component';
import { RegistrationComponent } from './pages/registration/registration.component';
import { RecoveryComponent } from './pages/recovery/recovery.component';
import { ChangePasswordComponent } from './pages/change-password/change-password.component';
import { HomepagePostsComponent } from './pages/homepage-posts/homepage-posts.component';
import { NewPostComponent } from './pages/new-post/new-post.component';
import { UpdateProfileComponent } from './pages/update-profile/update-profile.component';
import { CommunityLabelComponent } from './pages/community-label/community-label.component';
import { CommunitiesComponent } from './pages/communities/communities.component';
import { SearchComponent } from './pages/search/search.component';
import { EditPostComponent } from './pages/edit-post/edit-post.component';
import { PostDetailComponent } from './pages/post-detail/post-detail.component';
import { AuthorProfileComponent } from './pages/author-profile/author-profile.component';
import { BookmarksComponent } from './pages/bookmarks/bookmarks.component';
import { AuthGuard } from './services/auth.guard';

const routes: Routes = [
  { path: '', component: HomepageComponent },
  { path: 'homepage', redirectTo: '', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'registration', component: RegistrationComponent },
  { path: 'recovery', component: RecoveryComponent },
  { path: 'change-password', component: ChangePasswordComponent },
  { path: 'change-password/:user_id', redirectTo: 'change-password', pathMatch: 'full' },
  { path: 'explore', component: HomepagePostsComponent },
  { path: 'homepage-posts', redirectTo: 'explore', pathMatch: 'full' },
  { path: 'post/:slug', component: PostDetailComponent },
  { path: 'author/:username', component: AuthorProfileComponent },
  { path: 'my-posts', component: HomepagePostsComponent, canActivate: [AuthGuard], data: { onlyUserPosts: true } },
  { path: 'bookmarks', component: BookmarksComponent, canActivate: [AuthGuard] },
  { path: 'new-post', component: NewPostComponent, canActivate: [AuthGuard] },
  { path: 'edit-post/:id', component: EditPostComponent, canActivate: [AuthGuard] },
  { path: 'search', component: SearchComponent },
  { path: 'community/:label', component: CommunityLabelComponent },
  { path: 'communities', component: CommunitiesComponent },
  { path: 'update-profile', component: UpdateProfileComponent, canActivate: [AuthGuard] },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
