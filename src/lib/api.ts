import { useQuery } from '@tanstack/react-query';
import { getApiUrl } from '../utils/env';

/**
 * API communication layer
 * 
 * This module handles all external API requests and provides
 * fallback mock data when the API is unavailable (local-first approach)
 * 
 * Using relative paths allows deployment flexibility without hardcoding domains
 */

/**
 * Represents a news post/article fetched from the API or RSS feeds.
 * @property id - Unique identifier for the post (optional).
 * @property source - The source or publisher of the post.
 * @property platform - The platform type (e.g., Blog, RSS).
 * @property url - The URL to the original post.
 * @property title - The title of the post (optional).
 * @property content - The full content of the post.
 * @property summary - A summary of the post (optional).
 * @property timestamp - The publication timestamp (ISO string).
 * @property thumbnail - URL to a thumbnail image (optional).
 * @property author - The author of the post (optional).
 * @property created_at - Creation timestamp (optional).
 * @property updated_at - Last update timestamp (optional).
 * @property tags - List of tags associated with the post (optional).
 * @property category - Category of the post (optional).
 * @property tag_status - Tagging status: pending, tagged, or error (optional).
 */
export interface Post {
  id?: number;
  source: string;
  platform: string;
  url: string;
  title?: string;
  content: string;
  summary?: string;
  timestamp: string;
  thumbnail?: string;
  author?: string;
  created_at?: string;
  updated_at?: string;
  tags?: string[];
  category?: string;
  tag_status?: string; // Tagging flag: pending, tagged, error
}

export const API_BASE_URL = getApiUrl();

/**
 * Fetches AI news articles from the API.
 * Attempts to fetch from the remote API, falls back to localStorage cache, and finally mock data if all else fails.
 * @returns Promise resolving to an array of Post objects.
 */
export async function fetchPosts(): Promise<Post[]> {
  try {
    // First attempt to fetch from the API
    const response = await fetch(`${API_BASE_URL}/posts`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch posts: ${response.status}`);
    }
    
    const data = await response.json();
    // Save to localStorage for offline use
    try {
      localStorage.setItem('cachedPosts', JSON.stringify(data.data));
    } catch (e) {
      // Ignore localStorage errors
    }
    return data.data;
  } catch (error) {
    console.error('Error fetching posts:', error);
    // Try to load from localStorage before falling back to mock data
    try {
      const cached = localStorage.getItem('cachedPosts');
      if (cached) {
        const posts = JSON.parse(cached);
        if (Array.isArray(posts) && posts.length > 0) {
          return posts;
        }
      }
    } catch (e) {
      // Ignore localStorage errors
    }
    // Return mock data as fallback when API fails and no cache
    return [
      {
        id: 1,
        source: "OpenAI Blog",
        platform: "Blog",
        url: "https://example.com/openai-gpt5",
        title: "OpenAI Releases GPT-5 with Enhanced Reasoning Capabilities",
        content: "The latest iteration of GPT focuses on logical reasoning and mathematical problem solving, addressing previous limitations in complex cognitive tasks.",
        summary: "The latest iteration of GPT focuses on logical reasoning and mathematical problem solving, addressing previous limitations in complex cognitive tasks.",
        timestamp: new Date().toISOString(),
        thumbnail: "https://placehold.co/64x64?text=OpenAI",
        author: "OpenAI Team"
      },
      {
        id: 2,
        source: "Google AI Blog",
        platform: "Blog",
        url: "https://example.com/deepmind-protein",
        title: "Google DeepMind's Breakthrough in Protein Folding Accelerates Drug Discovery",
        content: "New advancements in AlphaFold technology have made protein structure prediction even more accurate, potentially reducing drug development timelines by years.",
        summary: "New advancements in AlphaFold technology have made protein structure prediction even more accurate, potentially reducing drug development timelines by years.",
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        thumbnail: "https://placehold.co/64x64?text=DeepMind",
        author: "DeepMind Research Team"
      },
      {
        id: 3,
        source: "Meta AI",
        platform: "Blog",
        url: "https://example.com/meta-llama3",
        title: "Meta's LLAMA 3 Goes Open Source",
        content: "Meta has released their latest large language model to the public, allowing researchers and companies to build on top of their work with fewer restrictions.",
        summary: "Meta has released their latest large language model to the public, allowing researchers and companies to build on top of their work with fewer restrictions.",
        timestamp: new Date(Date.now() - 172800000).toISOString(),
        thumbnail: "https://placehold.co/64x64?text=Meta",
        author: "Meta AI Team"
      },
      {
        id: 4,
        source: "Anthropic Research",
        platform: "Blog",
        url: "https://example.com/claude3-benchmark",
        title: "New Benchmark Shows Anthropic Claude 3 Outperforming GPT-4 on Complex Reasoning Tasks",
        content: "Recent evaluations suggest Claude 3 has superior performance in areas requiring nuanced understanding of context and multi-step reasoning problems.",
        summary: "Recent evaluations suggest Claude 3 has superior performance in areas requiring nuanced understanding of context and multi-step reasoning problems.",
        timestamp: new Date(Date.now() - 259200000).toISOString(),
        thumbnail: "https://placehold.co/64x64?text=Anthropic",
        author: "Anthropic Research Team"
      },
      {
        id: 5,
        source: "AI Safety Center",
        platform: "Blog",
        url: "https://example.com/ai-safety-framework",
        title: "AI Safety Researchers Propose New Framework for Model Evaluation",
        content: "A coalition of AI safety organizations has published guidelines for evaluating large language models before deployment, emphasizing transparency and risk assessment.",
        summary: "A coalition of AI safety organizations has published guidelines for evaluating large language models before deployment, emphasizing transparency and risk assessment.",
        timestamp: new Date(Date.now() - 345600000).toISOString(),
        thumbnail: "https://placehold.co/64x64?text=AI+Safety",
        author: "AI Safety Research Team"
      }
    ];
  }
}

/**
 * Sends a user question to the AI assistant and returns the response.
 * If the API is unavailable, returns a polite offline message.
 * @param message - The user's question to send to the assistant.
 * @returns Promise resolving to the assistant's response as a string.
 */
export async function sendChatMessage(message: string): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: message }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to send chat message: ${response.status}`);
    }
    
    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('Error sending chat message:', error);
    return "I'm currently offline. Please try again later when I'm connected to the server.";
  }
}

/**
 * React Query hook to fetch and cache posts from a given RSS feed URL.
 * @param url - The RSS feed URL.
 * @param source - The source or publisher name.
 * @param platform - The platform type (default: 'RSS').
 * @returns React Query result containing an array of Post objects.
 */
export const useRSSFeed = (url: string, source: string, platform: string = 'RSS') => {
  return useQuery<Post[]>({
    queryKey: ['rss', url, source, platform],
    queryFn: async () => {
      const response = await fetch(
        `${API_BASE_URL}/scrape/rss?${new URLSearchParams({
          url,
          source,
          platform,
        })}`
      );
      if (!response.ok) {
        throw new Error('Failed to fetch RSS feed');
      }
      const data = await response.json();
      return data.data;
    },
  });
};

/**
 * Imports an RSS feed by sending its details to the backend for scraping and saving.
 * @param url - The RSS feed URL.
 * @param source - The source or publisher name.
 * @param platform - The platform type (default: 'RSS').
 * @returns Promise resolving to the backend response.
 */
export async function importRssFeed(url: string, source: string, platform: string = "RSS") {
  const response = await fetch(`${API_BASE_URL}/scrape/rss/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, source, platform }),
  });
  if (!response.ok) {
    throw new Error("Failed to import RSS feed");
  }
  return await response.json();
}
