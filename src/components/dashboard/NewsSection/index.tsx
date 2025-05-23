import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { NewsList } from './NewsList';
import { Post, NewsArticle } from '../types';

export function NewsSection() {
  const [news, setNews] = useState<Post[]>([]);
  const [loadingNews, setLoadingNews] = useState(true);
  const [newsVisibleCount, setNewsVisibleCount] = useState(10);

  useEffect(() => {
    fetch("/api/posts")
      .then((res) => res.json())
      .then((data) => {
        setNews(data.data || []);
      })
      .finally(() => setLoadingNews(false));
  }, []);

  const todaysNews = news.filter((post) => {
    const postDate = new Date(post.timestamp);
    const now = new Date();
    return postDate.getFullYear() === now.getFullYear() &&
      postDate.getMonth() === now.getMonth() &&
      postDate.getDate() === now.getDate();
  });

  const newsArticles: NewsArticle[] = todaysNews
    .slice(0, newsVisibleCount)
    .map((post) => ({
      id: post.id?.toString() ?? post.url,
      title: post.title || "Untitled",
      summary: post.summary || post.content?.slice(0, 120) + "...",
      date: new Date(post.timestamp).toLocaleDateString() +
        " " +
        new Date(post.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false }),
      source: post.source,
      url: post.url,
    }));

  const canLoadMoreNews = newsVisibleCount < todaysNews.length;

  return (
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
          <>
            <NewsList articles={newsArticles} />
            {canLoadMoreNews && (
              <div className="flex justify-center mt-4">
                <button
                  className="px-4 py-2 bg-primary text-white rounded hover:bg-primary/80 transition"
                  onClick={() => setNewsVisibleCount((c) => c + 10)}
                >
                  Load More
                </button>
              </div>
            )}
          </>
        )}
      </Card>
    </section>
  );
} 