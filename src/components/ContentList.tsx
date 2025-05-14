import { useRSSFeed } from '@/lib/api';
import { PostCard } from './PostCard';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

interface ContentListProps {
  type: 'rss' | 'ws';
  url?: string;
  source?: string;
  platform?: string;
}

/**
 * ContentList component displays a list of posts from an RSS or webscraped source.
 *
 * @param type - 'rss' or 'ws' (webscraped)
 * @param url - Feed URL (for RSS)
 * @param source - Source name (for RSS)
 * @param platform - Platform type (optional)
 */
export function ContentList({ type, url, source, platform }: ContentListProps) {
  if (type === 'rss' && url && source) {
    const { data: posts, isLoading, error } = useRSSFeed(url, source, platform);

    if (isLoading) {
      return <FeedSkeleton />;
    }

    if (error) {
      return (
        <div className="text-red-500">
          Error loading feed: {(error as Error).message}
        </div>
      );
    }

    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {posts?.map((post) => (
          <PostCard key={post.url} post={post} />
        ))}
      </div>
    );
  }

  if (type === 'ws') {
    // TODO: Implement webscraped content list
    return (
      <div className="text-muted-foreground">
        Webscraped content coming soon...
      </div>
    );
  }

  return null;
}

/**
 * FeedSkeleton component displays loading skeletons for the content list.
 */
function FeedSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <Card key={i}>
          <CardHeader>
            <Skeleton className="h-4 w-3/4" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-4 w-2/3" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
} 