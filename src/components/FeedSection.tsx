import { useRSSFeed, Post } from '@/lib/api';
import { PostCard } from './PostCard';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

interface FeedSectionProps {
  url: string;
  source: string;
  platform?: string;
}

/**
 * FeedSection component displays a section of posts from a single RSS feed source.
 *
 * @param url - Feed URL
 * @param source - Source name
 * @param platform - Platform type (optional)
 */
export function FeedSection({
  url,
  source,
  platform,
}: FeedSectionProps) {
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

/**
 * FeedSkeleton component displays loading skeletons for the feed section.
 */
function FeedSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <Card key={i}>
          <CardHeader>
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/4 mt-2" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3 mt-2" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
} 