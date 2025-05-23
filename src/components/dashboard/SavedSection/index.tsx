import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bookmark } from 'lucide-react';
import { SavedPost } from '../types';

function SavedItem({ item }: { item: SavedPost }) {
  const post = item.post;
  return (
    <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted transition-colors relative">
      <div className="flex-shrink-0 mt-1">
        <Bookmark className="h-4 w-4 text-blue-500" />
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
            {new Date(post.timestamp).toLocaleDateString()} {new Date(post.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false })}
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
            Saved {new Date(item.saved_at).toLocaleDateString()} {new Date(item.saved_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false })}
          </span>
        </div>
      </div>
    </div>
  );
}

function SavedList({ items }: { items: SavedPost[] }) {
  return (
    <div className="space-y-1">
      {items.map((item) => (
        <SavedItem key={item.id} item={item} />
      ))}
    </div>
  );
}

interface Props {
  saved: SavedPost[];
  loadingSaved: boolean;
}

const SavedSection: React.FC<Props> = ({ saved, loadingSaved }) => {
  return (
    <>
      {loadingSaved ? (
        <div>Loading...</div>
      ) : saved.length === 0 ? (
        <div className="text-muted-foreground">No saved posts yet.</div>
      ) : (
        <Card className="p-4">
          <SavedList items={saved} />
        </Card>
      )}
    </>
  );
};

export default SavedSection; 