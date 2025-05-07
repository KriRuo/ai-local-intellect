
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { CalendarIcon, CircleIcon } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { Post } from "@/lib/store";

interface PostCardProps {
  post: Post;
}

export function PostCard({ post }: PostCardProps) {
  const formattedDate = formatDistanceToNow(
    new Date(post.published_at),
    { addSuffix: true }
  );

  return (
    <Card className="overflow-hidden transition-all hover:shadow-md">
      <CardHeader className="p-4 pb-2 flex flex-row justify-between items-start">
        <div>
          <h3 className="font-semibold text-lg leading-tight line-clamp-2">
            <a 
              href={post.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-primary transition-colors"
            >
              {post.title}
            </a>
          </h3>
        </div>
      </CardHeader>
      <CardContent className="p-4 pt-1">
        <p className="text-sm text-muted-foreground line-clamp-3 mb-3">
          {post.summary}
        </p>
        <div className="flex flex-wrap gap-2">
          {post.tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
          {post.tags.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{post.tags.length - 3} more
            </Badge>
          )}
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0 flex justify-between items-center text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <CircleIcon className="h-3 w-3" />
          <span>{post.source}</span>
        </div>
        <div className="flex items-center gap-1">
          <CalendarIcon className="h-3 w-3" />
          <span>{formattedDate}</span>
        </div>
      </CardFooter>
    </Card>
  );
}
