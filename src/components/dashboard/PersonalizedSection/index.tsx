import * as React from 'react';
import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bookmark } from 'lucide-react';
import { Post, PersonalizedPost } from '../types';
import { validatePost } from '@/utils/validation';
import { logger } from '@/lib/logger';
import { SCORING } from '@/constants/scoring';

/**
 * Custom error for post validation failures
 */
class PostValidationError extends Error {
  constructor(message: string, public post: Post) {
    super(message);
    this.name = 'PostValidationError';
  }
}

/**
 * Calculates a relevance score for a post based on user preferences
 * @param post - The post to score
 * @param preferredTopics - User's preferred topics
 * @param preferredSources - User's preferred sources
 * @returns Object containing score and justification
 * @throws {PostValidationError} If post data is invalid
 */
function calculatePostScore(
  post: Post, 
  preferredTopics: string[], 
  preferredSources: string[]
): { score: number, justification: string } {
  if (!validatePost(post)) {
    throw new PostValidationError('Invalid post data', post);
  }
  let score = SCORING.BASE_SCORE;
  const matchedTopics = post.tags?.filter((tag) => preferredTopics.includes(tag)) || [];
  const sourceMatch = preferredSources.includes(post.source);
  
  if (matchedTopics.length > 0) score += SCORING.TOPIC_MATCH_BONUS;
  if (sourceMatch) score += SCORING.SOURCE_MATCH_BONUS;
  
  return { 
    score, 
    justification: buildJustification(matchedTopics, post.source, sourceMatch)
  };
}

/**
 * Builds a human-readable justification for the post's score
 */
function buildJustification(
  matchedTopics: string[], 
  source: string, 
  sourceMatch: boolean
): string {
  if (matchedTopics.length > 0 && sourceMatch) {
    return `Matches preferred topic '${matchedTopics[0]}' and source '${source}'.`;
  }
  if (matchedTopics.length > 0) {
    return `Matches preferred topic '${matchedTopics[0]}'.`;
  }
  if (sourceMatch) {
    return `Matches preferred source '${source}'.`;
  }
  return "No preferred topics or sources matched.";
}

/**
 * Computes personalized posts by scoring and sorting them based on user preferences
 * @param posts - List of posts to personalize
 * @param preferredTopics - User's preferred topics
 * @param preferredSources - User's preferred sources
 * @returns Sorted array of personalized posts
 */
export function computePersonalizedPosts(
  posts: Post[],
  preferredTopics: string[],
  preferredSources: string[]
): PersonalizedPost[] {
  try {
    const scoredPosts = posts.map(post => {
      try {
        const { score, justification } = calculatePostScore(
          post, 
          preferredTopics, 
          preferredSources
        );
        return { post, relevance_score: score, justification };
      } catch (error) {
        if (error instanceof PostValidationError) {
          logger.warn('Invalid post skipped:', error.post);
          return { 
            post, 
            relevance_score: SCORING.BASE_SCORE, 
            justification: "Invalid post data" 
          };
        }
        throw error;
      }
    });

    const sortedPosts = scoredPosts.sort((a, b) => b.relevance_score - a.relevance_score);

    if (process.env.NODE_ENV === 'development' && sortedPosts.length > 0) {
      logger.debug('Highest scoring post:', sortedPosts[0]);
    }

    return sortedPosts;
  } catch (error) {
    logger.error('Error computing personalized posts:', error);
    return [];
  }
}

/**
 * Props for PersonalizedContentSection
 * @property posts List of posts to personalize
 * @property preferredTopics User's preferred topics
 * @property preferredSources User's preferred sources
 */
interface Props {
  posts: Post[];
  preferredTopics: string[];
  preferredSources: string[];
}

/**
 * PersonalizedContentSection component
 * Displays posts personalized to the user's preferences, sorted by relevance.
 * Allows incremental loading of more posts.
 */
const PersonalizedContentSection: React.FC<Props> = ({ posts, preferredTopics, preferredSources }) => {
  const [visibleCount, setVisibleCount] = useState(10);
  // Compute personalized posts based on preferences
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