import { Post } from '@/components/dashboard/types';

/**
 * Validates a post object to ensure it has all required fields and correct types
 * @param post - The post object to validate
 * @returns boolean indicating if the post is valid
 */
export function validatePost(post: Post): boolean {
  return post && 
         typeof post === 'object' && 
         Array.isArray(post.tags) && 
         typeof post.source === 'string' &&
         typeof post.timestamp === 'string' &&
         typeof post.url === 'string' &&
         (typeof post.title === 'string' || post.title === undefined) &&
         (typeof post.summary === 'string' || post.summary === undefined) &&
         (typeof post.content === 'string' || post.content === undefined);
} 