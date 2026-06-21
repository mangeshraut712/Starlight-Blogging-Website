export class Post {
  id?: number;
  slug?: string;
  author_name?: string;
  author_id?: number;
  title?: string;
  created_at?: string;
  updated_at?: string;
  content?: string;
  excerpt?: string;
  cover_image?: string;
  label?: string;
  likes?: number;
  view_count?: number;
  status?: string;
}

export interface PaginatedPosts {
  posts: Post[];
  page: number;
  per_page: number;
  total: number;
  has_more: boolean;
}
