import { Post } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';

interface PostCardProps {
  post: Post;
}

export function PostCard({ post }: PostCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold line-clamp-2">
            <a
              href={post.url}
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors duration-150 hover:underline hover:text-blue-600 focus:underline focus:text-blue-600"
            >
              {post.title || 'Untitled'}
            </a>
          </CardTitle>
          <Badge variant="outline">{post.source}</Badge>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>{post.platform}</span>
          <span>•</span>
          <span>{formatDistanceToNow(new Date(post.timestamp), { addSuffix: true })}</span>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-3">
          {post.content}
        </p>
        {post.thumbnail && (
          <img
            src={post.thumbnail}
            alt={post.title}
            className="mt-4 rounded-md w-full h-48 object-cover"
          />
        )}
      </CardContent>
    </Card>
  );
}
