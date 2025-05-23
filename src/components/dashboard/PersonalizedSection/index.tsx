import * as React from 'react';
import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bookmark } from 'lucide-react';
import { Post, PersonalizedPost } from '../types';

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

interface Props {
  posts: Post[];
  preferredTopics: string[];
  preferredSources: string[];
}

const PersonalizedContentSection: React.FC<Props> = ({ posts, preferredTopics, preferredSources }) => {
  const [visibleCount, setVisibleCount] = useState(10);
  const personalized = computePersonalizedPosts(posts, preferredTopics, preferredSources);
  const canLoadMore = visibleCount < personalized.length;

  return (
    <Card className="p-4">
      {personalized.length === 0 ? (
        <div className="text-muted-foreground">No personalized content found.</div>
      ) : (
        <>
          <div className="space-y-1">
            {personalized.slice(0, visibleCount).map(({ post, relevance_score, justification }) => (
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
                      {new Date(post.timestamp).toLocaleDateString()} {new Date(post.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false })}
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
          {canLoadMore && (
            <div className="flex justify-center mt-4">
              <button
                className="px-4 py-2 bg-primary text-white rounded hover:bg-primary/80 transition"
                onClick={() => setVisibleCount((c) => c + 10)}
              >
                Load More
              </button>
            </div>
          )}
        </>
      )}
    </Card>
  );
};

export default PersonalizedContentSection; 