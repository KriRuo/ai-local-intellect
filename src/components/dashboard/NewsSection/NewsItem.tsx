import { NewsArticle } from '../types';
import { Newspaper } from 'lucide-react';

export function NewsItem({ article }: { article: NewsArticle }) {
  return (
    <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted transition-colors relative">
      <div className="flex-shrink-0 mt-1">
        <Newspaper className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between">
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-blue-600 hover:underline line-clamp-1"
          >
            {article.title}
          </a>
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