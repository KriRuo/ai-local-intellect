import * as React from "react";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { PostCard } from "@/components/PostCard";
import { Bookmark, Clock, ExternalLink, Newspaper } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

// Types for saved and news posts
interface Post {
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

interface SavedPost {
  id: number;
  post_id: number;
  saved_at: string;
  post: Post;
}

// NewsArticle interface for news items
interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  date: string;
  source: string;
  url: string;
}

// NewsItem component for individual news entries
function NewsItem({ article }: { article: NewsArticle }) {
  return (
    <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted transition-colors relative">
      <div className="flex-shrink-0 mt-1">
        <Newspaper className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between">
          {/* Title as link */}
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-blue-600 hover:underline line-clamp-1"
          >
            {article.title}
          </a>
          {/* Published date (top right) */}
          <span className="text-xs text-muted-foreground ml-4 whitespace-nowrap">
            {article.date}
          </span>
        </div>
        <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
          {article.summary}
        </p>
        <div className="flex items-center gap-2 mt-2">
          <span className="text-xs text-muted-foreground">{article.source}</span>
        </div>
      </div>
    </div>
  );
}

// NewsList component for the news section
function NewsList({ articles }: { articles: NewsArticle[] }) {
  return (
    <div className="space-y-1">
      {articles.map((article) => (
        <NewsItem key={article.id} article={article} />
      ))}
    </div>
  );
}

// SavedItem component for individual saved post entries
function SavedItem({ item }: { item: SavedPost }) {
  const post = item.post;
  return (
    <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted transition-colors relative">
      <div className="flex-shrink-0 mt-1">
        <Bookmark className="h-4 w-4 text-blue-500" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between">
          {/* Title as link */}
          <a
            href={post.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-blue-600 hover:underline line-clamp-1"
          >
            {post.title || "Untitled"}
          </a>
          {/* Published date (top right) */}
          <span className="text-xs text-muted-foreground ml-4 whitespace-nowrap">
            {new Date(post.timestamp).toLocaleDateString()} {new Date(post.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </span>
        </div>
        <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
          {post.summary || post.content?.slice(0, 120) + "..."}
        </p>
        <div className="flex items-center gap-2 mt-2 flex-wrap">
          {post.tags && post.tags.length > 0 && post.tags.map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs bg-muted/60 border-muted-foreground/20 text-muted-foreground">
              {tag}
            </Badge>
          ))}
          <span className="text-xs text-muted-foreground ml-auto">
            Saved {new Date(item.saved_at).toLocaleDateString()} {new Date(item.saved_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </span>
        </div>
      </div>
    </div>
  );
}

// SavedList component for the saved content section
function SavedList({ items }: { items: SavedPost[] }) {
  return (
    <div className="space-y-1">
      {items.map((item) => (
        <SavedItem key={item.id} item={item} />
      ))}
    </div>
  );
}

// SummarySection component for the middle section
function SummarySection() {
  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-4">Summary (Today | This Week)</h2>
      <div className="space-y-4">
        <div className="h-24 bg-muted rounded-md animate-pulse" />
        <div className="space-y-2">
          <div className="h-4 bg-muted rounded-md w-3/4 animate-pulse" />
          <div className="h-4 bg-muted rounded-md animate-pulse" />
          <div className="h-4 bg-muted rounded-md w-5/6 animate-pulse" />
        </div>
      </div>
      <div className="mt-4 text-sm text-muted-foreground">
        Summary content will appear here
      </div>
    </Card>
  );
}

// --- Personalized Content Section Types and Logic ---

interface PersonalizedPost {
  post: Post;
  relevance_score: number;
  justification: string;
}

function computePersonalizedPosts(
  posts: Post[],
  preferredTopics: string[],
  preferredSources: string[]
): PersonalizedPost[] {
  return posts.map((post) => {
    let score = 1;
    let justification = "No preferred topics or sources matched.";
    const matchedTopics = post.tags?.filter((tag) => preferredTopics.includes(tag)) || [];
    const sourceMatch = preferredSources.includes(post.source);
    if (matchedTopics.length > 0) score += 2;
    if (sourceMatch) score += 3;
    if (score > 5) score = 5;
    if (matchedTopics.length > 0 && sourceMatch) {
      justification = `Matches preferred topic '${matchedTopics[0]}' and source '${post.source}'.`;
    } else if (matchedTopics.length > 0) {
      justification = `Matches preferred topic '${matchedTopics[0]}'.`;
    } else if (sourceMatch) {
      justification = `Matches preferred source '${post.source}'.`;
    }
    return { post, relevance_score: score, justification };
  }).sort((a, b) => b.relevance_score - a.relevance_score);
}

function PersonalizedContentSection({ posts, preferredTopics, preferredSources }: { posts: Post[], preferredTopics: string[], preferredSources: string[] }) {
  const personalized = computePersonalizedPosts(posts, preferredTopics, preferredSources).slice(0, 5);
  return (
    <Card className="p-4">
      {personalized.length === 0 ? (
        <div className="text-muted-foreground">No personalized content found.</div>
      ) : (
        <div className="space-y-1">
          {personalized.map(({ post, relevance_score, justification }) => (
            <div key={post.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted transition-colors relative">
              <div className="flex-shrink-0 mt-1">
                <Bookmark className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <a
                    href={post.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-blue-600 hover:underline line-clamp-1"
                  >
                    {post.title || "Untitled"}
                  </a>
                  <span className="text-xs text-muted-foreground ml-4 whitespace-nowrap">
                    {new Date(post.timestamp).toLocaleDateString()} {new Date(post.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                  {post.summary || post.content?.slice(0, 120) + "..."}
                </p>
                <div className="text-xs text-muted-foreground mt-1 mb-1">
                  {post.source}
                </div>
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  {post.tags && post.tags.length > 0 && post.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs bg-muted/60 border-muted-foreground/20 text-muted-foreground">
                      {tag}
                    </Badge>
                  ))}
                  <span className="inline-block bg-primary/90 text-white text-xs font-bold px-2 py-1 rounded shadow ml-auto">
                    Score: {relevance_score}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

// Main Dashboard component
export default function Dashboard() {
  // Saved posts state
  const [saved, setSaved] = useState<SavedPost[]>([]);
  const [loadingSaved, setLoadingSaved] = useState(true);
  // News posts state
  const [news, setNews] = useState<Post[]>([]);
  const [loadingNews, setLoadingNews] = useState(true);
  // User preferences state
  const [preferredSources, setPreferredSources] = useState<string[]>([]);
  const [preferredTopics, setPreferredTopics] = useState<string[]>([]);
  const [loadingPrefs, setLoadingPrefs] = useState(true);

  useEffect(() => {
    // Fetch saved posts
    fetch("/api/saved")
      .then((res) => res.json())
      .then(setSaved)
      .finally(() => setLoadingSaved(false));
    // Fetch most recent posts
    fetch("/api/posts")
      .then((res) => res.json())
      .then((data) => setNews(data.data?.slice(0, 10) || []))
      .finally(() => setLoadingNews(false));
    // Fetch user preferences
    fetch("/api/preferences")
      .then((res) => res.json())
      .then((prefs) => {
        setPreferredSources(prefs.preferred_sources || []);
        setPreferredTopics(prefs.preferred_categories || []);
      })
      .finally(() => setLoadingPrefs(false));
  }, []);

  // Convert news posts to NewsArticle format
  const newsArticles: NewsArticle[] = news.map((post) => ({
    id: post.id?.toString() ?? post.url,
    title: post.title || "Untitled",
    summary: post.summary || post.content?.slice(0, 120) + "...",
    date: new Date(post.timestamp).toLocaleDateString() +
      " " +
      new Date(post.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    source: post.source,
    url: post.url,
  }));

  return (
    <div className="container mx-auto py-6 space-y-8">
      {/* News Section (moved to top) */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">Most Recent News</h2>
        </div>
        <Card className="p-4">
          {loadingNews ? (
            <div>Loading...</div>
          ) : newsArticles.length === 0 ? (
            <div className="text-muted-foreground">No news found.</div>
          ) : (
            <NewsList articles={newsArticles} />
          )}
        </Card>
      </section>

      {/* Personalized Content Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">Personalized Content</h2>
        </div>
        {loadingNews || loadingPrefs ? (
          <div>Loading...</div>
        ) : news.length === 0 ? (
          <div className="text-muted-foreground">No personalized posts found.</div>
        ) : (
          <PersonalizedContentSection posts={news} preferredTopics={preferredTopics} preferredSources={preferredSources} />
        )}
      </section>

      {/* Saved Content Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">Saved Content</h2>
        </div>
        {loadingSaved ? (
          <div>Loading...</div>
        ) : saved.length === 0 ? (
          <div className="text-muted-foreground">No saved posts yet.</div>
        ) : (
          <Card className="p-4">
            <SavedList items={saved} />
          </Card>
        )}
      </section>

      {/* Summary Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">Summary</h2>
        </div>
        <SummarySection />
      </section>
    </div>
  );
} 