export interface Post {
  id: number;
  title: string;
  content: string;
  summary?: string;
  tags?: string[];
  timestamp: string;
  source: string;
  platform: string;
  url: string;
  thumbnail?: string;
  category?: string;
}

export interface SavedPost {
  id: number;
  post_id: number;
  saved_at: string;
  post: Post;
}

export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  date: string;
  source: string;
  url: string;
}

export interface PersonalizedPost {
  post: Post;
  relevance_score: number;
  justification: string;
} 