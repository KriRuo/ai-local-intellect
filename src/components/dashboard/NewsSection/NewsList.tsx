import { NewsArticle } from '../types';
import { NewsItem } from './NewsItem';

export function NewsList({ articles }: { articles: NewsArticle[] }) {
  return (
    <div className="space-y-1">
      {articles.map((article) => (
        <NewsItem key={article.id} article={article} />
      ))}
    </div>
  );
} 