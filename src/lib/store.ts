
import { create } from 'zustand';

export type Post = {
  id: string;
  title: string;
  summary: string;
  url: string;
  published_at: string;
  tags: string[];
  source: string;
};

export type ChatMessage = {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
};

interface AppState {
  posts: Post[];
  isLoadingPosts: boolean;
  postError: string | null;
  chatMessages: ChatMessage[];
  isLoadingChat: boolean;
  chatError: string | null;
  setPosts: (posts: Post[]) => void;
  setIsLoadingPosts: (isLoading: boolean) => void;
  setPostError: (error: string | null) => void;
  addChatMessage: (message: ChatMessage) => void;
  setIsLoadingChat: (isLoading: boolean) => void;
  setChatError: (error: string | null) => void;
  clearChatMessages: () => void;
}

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
