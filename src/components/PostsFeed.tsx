import { useEffect, useState, useRef } from "react";
import { PostCard } from "@/components/PostCard";
import { useAppStore } from "@/lib/store";
import { fetchPosts } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { FilterIcon, ChevronDown, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { DropdownMenu, DropdownMenuCheckboxItem, DropdownMenuContent, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

/**
 * Loading skeleton for post cards
 * Mimics the structure of PostCard for a smoother visual transition
 */
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

function RSSFilter({ sources, onFilterChange, className = "" }) {
  const [selectedSources, setSelectedSources] = useState([]);
  const [open, setOpen] = useState(false);

  // Sort sources alphabetically by name
  const sortedSources = [...sources].sort((a, b) => a.name.localeCompare(b.name));

  const handleSourceToggle = (sourceId) => {
    setSelectedSources((current) => {
      const newSelection = current.includes(sourceId)
        ? current.filter((id) => id !== sourceId)
        : [...current, sourceId];
      return newSelection;
    });
  };

  const clearAllFilters = () => {
    setSelectedSources([]);
  };

  useEffect(() => {
    onFilterChange(selectedSources);
  }, [selectedSources, onFilterChange]);

  return (
    <div className={cn("flex flex-col space-y-2", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FilterIcon size={16} className="text-muted-foreground" />
          <span className="text-sm font-medium">Filter Sources</span>
        </div>
        {selectedSources.length > 0 && (
          <Button variant="ghost" size="sm" onClick={clearAllFilters} className="h-8 px-2 text-xs">
            Clear all
          </Button>
        )}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <DropdownMenu open={open} onOpenChange={setOpen}>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="h-9">
              {selectedSources.length > 0 ? `${selectedSources.length} selected` : "Select sources"}
              <ChevronDown className="ml-2 h-4 w-4 opacity-60" aria-hidden="true" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56 max-h-64 overflow-y-auto" align="start">
            {sortedSources.map((source) => (
              <DropdownMenuCheckboxItem
                key={source.id}
                checked={selectedSources.includes(source.id)}
                onCheckedChange={() => handleSourceToggle(source.id)}
              >
                {source.name}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
        {selectedSources.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedSources.map((sourceId) => {
              const source = sources.find((s) => s.id === sourceId);
              if (!source) return null;
              return (
                <Badge key={sourceId} variant="secondary" className="px-2 py-1 h-9">
                  {source.name}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSourceToggle(sourceId)}
                    className="h-auto w-auto p-0 ml-1"
                  >
                    <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                    <span className="sr-only">Remove {source.name} filter</span>
                  </Button>
                </Badge>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * PostsFeed component manages the display of AI news articles
 * 
 * Features:
 * 1. Auto-fetches articles on component mount
 * 2. Displays loading skeletons during API requests
 * 3. Handles error states with user-friendly messages
 * 4. Provides retry functionality when loading fails
 * 5. Shows toast notifications for loading success/failure
 */
export function PostsFeed() {
  const { posts, isLoadingPosts, postError, setPosts, setIsLoadingPosts, setPostError } = useAppStore();
  const [page, setPage] = useState(1);
  const [filteredSources, setFilteredSources] = useState([]);
  const POSTS_PER_PAGE = 20;
  const feedRef = useRef<HTMLDivElement>(null);

  // Fetches posts from API with loading states and error handling
  const loadPosts = async () => {
    setIsLoadingPosts(true);
    setPostError(null);
    
    try {
      const fetchedPosts = await fetchPosts();
      setPosts(fetchedPosts); // Store posts as-is from API
      
      // Show success toast if posts were loaded
      if (fetchedPosts && fetchedPosts.length > 0) {
        toast.success(`Loaded ${fetchedPosts.length} articles`);
      } else {
        toast.info("No new articles found");
      }
    } catch (error) {
      setPostError(error instanceof Error ? error.message : "Failed to load posts");
      console.error("Error loading posts:", error);
      toast.error("Failed to load articles");
    } finally {
      setIsLoadingPosts(false);
    }
  };

  // Load posts on component mount
  useEffect(() => {
    loadPosts();
  }, []);

  // Scroll to top of feed when page changes
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [page]);

  // Get unique sources from posts
  const uniqueSources = Array.from(
    new Set(posts.map((p) => p.source))
  ).map((source) => ({ id: source, name: source }));

  // Filter posts by selected sources
  const filteredPosts =
    filteredSources.length === 0
      ? posts
      : posts.filter((post) => filteredSources.includes(post.source));

  // Pagination logic
  const totalPages = Math.ceil(filteredPosts.length / POSTS_PER_PAGE);
  const paginatedPosts = filteredPosts.slice((page - 1) * POSTS_PER_PAGE, page * POSTS_PER_PAGE);

  // Error state view
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

  // Loading state view
  if (isLoadingPosts) {
    return (
      <div className="space-y-6">
        {Array.from({ length: 3 }).map((_, index) => (
          <PostCardSkeleton key={`skeleton-${index}`} />
        ))}
      </div>
    );
  }

  // Main content view with filter and pagination
  return (
    <div className="space-y-6" ref={feedRef}>
      <RSSFilter sources={uniqueSources} onFilterChange={setFilteredSources} />
      {filteredPosts.length === 0 ? (
        <div className="text-center p-10 bg-white rounded-2xl shadow-sm">
          <p className="text-muted-foreground">No articles available</p>
        </div>
      ) : (
        <>
          {paginatedPosts.map((post) => (
            <PostCard key={post.id?.toString() ?? post.url} post={post} />
          ))}
          <div className="flex justify-center items-center gap-4 mt-6">
            <Button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              variant="outline"
            >
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {page} of {totalPages}
            </span>
            <Button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              variant="outline"
            >
              Next
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
