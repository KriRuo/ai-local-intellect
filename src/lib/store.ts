
import { create } from 'zustand';

/**
 * Post interface defines the structure of an article in the news feed
 */
export type Post = {
  id: string;
  title: string;
  summary: string;
  url: string;
  published_at: string;
  tags: string[];
  source: string;
};

/**
 * ChatMessage interface defines the structure of messages in the AI assistant
 */
export type ChatMessage = {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
};

/**
 * AppState interface defines the global state structure
 * The app uses two main domains:
 * 1. Posts management (news feed)
 * 2. Chat management (AI assistant)
 */
interface AppState {
  // Posts domain
  posts: Post[];
  isLoadingPosts: boolean;
  postError: string | null;
  
  // Chat domain
  chatMessages: ChatMessage[];
  isLoadingChat: boolean;
  chatError: string | null;
  
  // Posts actions
  setPosts: (posts: Post[]) => void;
  setIsLoadingPosts: (isLoading: boolean) => void;
  setPostError: (error: string | null) => void;
  
  // Chat actions
  addChatMessage: (message: ChatMessage) => void;
  setIsLoadingChat: (isLoading: boolean) => void;
  setChatError: (error: string | null) => void;
  clearChatMessages: () => void;
}

/**
 * Global state store using Zustand
 * Enables components to access and update state without prop drilling
 */
export const useAppStore = create<AppState>((set) => ({
  posts: [],
  isLoadingPosts: false,
  postError: null,
  chatMessages: [],
  isLoadingChat: false,
  chatError: null,
  
  setPosts: (posts) => set({ posts }),
  setIsLoadingPosts: (isLoading) => set({ isLoadingPosts: isLoading }),
  setPostError: (error) => set({ postError: error }),
  
  addChatMessage: (message) => 
    set((state) => ({ 
      chatMessages: [...state.chatMessages, message] 
    })),
  
  setIsLoadingChat: (isLoading) => set({ isLoadingChat: isLoading }),
  setChatError: (error) => set({ chatError: error }),
  clearChatMessages: () => set({ chatMessages: [] }),
}));
