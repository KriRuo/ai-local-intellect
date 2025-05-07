
import { useEffect } from "react";
import { PostCard } from "@/components/PostCard";
import { useAppStore } from "@/lib/store";
import { fetchPosts } from "@/lib/api";
import { Button } from "@/components/ui/button"; // Fixed import from button.tsx instead of card.tsx
import { AlertCircle, RefreshCw } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

export function PostsFeed() {
  const { posts, isLoadingPosts, postError, setPosts, setIsLoadingPosts, setPostError } = useAppStore();

  const loadPosts = async () => {
    setIsLoadingPosts(true);
    setPostError(null);
    
    try {
      const fetchedPosts = await fetchPosts();
      setPosts(fetchedPosts);
      
      // Show success toast if posts were loaded
      if (fetchedPosts && fetchedPosts.length > 0) {
        toast.success(`Loaded ${fetchedPosts.length} articles`);
      } else {
        // If no posts are returned, show an info message
        toast.info("No new articles found");
        
        // Use mock posts for development to ensure we see something
        setPosts([
          {
            id: "1",
            title: "OpenAI Releases GPT-5 with Enhanced Reasoning Capabilities",
            summary: "The latest iteration of GPT focuses on logical reasoning and mathematical problem solving, addressing previous limitations in complex cognitive tasks.",
            tags: ["OpenAI", "GPT-5", "AI Models"],
            source: "OpenAI Blog",
            published_at: new Date().toISOString(),
            url: "https://example.com/openai-gpt5",
          },
          {
            id: "2",
            title: "Google DeepMind's Breakthrough in Protein Folding Accelerates Drug Discovery",
            summary: "New advancements in AlphaFold technology have made protein structure prediction even more accurate, potentially reducing drug development timelines by years.",
            tags: ["Google DeepMind", "AlphaFold", "Protein Folding", "Drug Discovery"],
            source: "Google AI Blog",
            published_at: new Date(Date.now() - 86400000).toISOString(),
            url: "https://example.com/deepmind-protein",
          },
          {
            id: "3",
            title: "Meta's LLAMA 3 Goes Open Source",
            summary: "Meta has released their latest large language model to the public, allowing researchers and companies to build on top of their work with fewer restrictions.",
            tags: ["Meta", "LLAMA 3", "Open Source", "LLM"],
            source: "Meta AI",
            published_at: new Date(Date.now() - 172800000).toISOString(),
            url: "https://example.com/meta-llama3",
          }
        ]);
      }
    } catch (error) {
      setPostError(error instanceof Error ? error.message : "Failed to load posts");
      console.error("Error loading posts:", error);
      toast.error("Failed to load articles");
    } finally {
      setIsLoadingPosts(false);
    }
  };

  useEffect(() => {
    loadPosts();
  }, []);

  if (postError) {
    return (
      <div className="flex flex-col items-center justify-center p-10 text-center bg-white rounded-2xl shadow-sm">
        <AlertCircle className="h-10 w-10 text-destructive mb-4" />
        <h3 className="text-xl font-medium mb-2">Failed to load posts</h3>
        <p className="text-muted-foreground mb-4">{postError}</p>
        <Button onClick={loadPosts} variant="outline" className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {isLoadingPosts 
        ? Array(3)
            .fill(0)
            .map((_, i) => <PostCardSkeleton key={i} />)
        : posts.map((post) => <PostCard key={post.id} post={post} />)
      }
      {!isLoadingPosts && posts.length === 0 && (
        <div className="text-center py-16 bg-white rounded-2xl shadow-sm">
          <p className="text-muted-foreground">No posts available yet.</p>
        </div>
      )}
    </div>
  );
}

function PostCardSkeleton() {
  return (
    <div className="border rounded-xl overflow-hidden shadow-sm bg-white">
      <div className="p-5 pb-2">
        <Skeleton className="h-6 w-3/4 mb-2" />
        <Skeleton className="h-6 w-1/2" />
      </div>
      <div className="p-5 pt-1">
        <Skeleton className="h-4 w-full mb-1" />
        <Skeleton className="h-4 w-full mb-1" />
        <Skeleton className="h-4 w-2/3 mb-3" />
        <div className="flex gap-2">
          <Skeleton className="h-5 w-16 rounded-full" />
          <Skeleton className="h-5 w-16 rounded-full" />
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
      </div>
      <div className="p-5 pt-0 flex justify-between">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-24" />
      </div>
    </div>
  );
}
