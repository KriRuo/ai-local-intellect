import * as React from "react";
import { cva } from "class-variance-authority";
import { formatDistanceToNow, format } from "date-fns";
import { ExternalLink, Clock, Globe } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { Post } from "@/lib/api";
import DOMPurify from "dompurify";
import { toZonedTime } from "date-fns-tz";

// Utility to strip HTML tags from a string
const stripHtml = (html: string) => html.replace(/<[^>]*>?/gm, "");
const truncateText = (text: string, maxLength: number) =>
  text.length <= maxLength ? text : text.slice(0, maxLength) + "...";

// Remove <img> tags from HTML content
const removeImages = (html: string) => html.replace(/<img[^>]*>/gi, "");

const postCardVariants = cva("group transition-all duration-300", {
  variants: {
    variant: {
      default: ["hover:shadow-md", "hover:-translate-y-1"],
      gradient: [
        "hover:shadow-lg",
        "hover:shadow-primary/10",
        "hover:-translate-y-1",
      ],
      lifted: [
        "shadow-[0px_2px_0px_0px_rgba(0,0,0,0.4)]",
        "dark:shadow-[0px_2px_0px_0px_rgba(255,255,255,0.3)]",
        "hover:shadow-[0px_4px_0px_0px_rgba(0,0,0,0.4)]",
        "dark:hover:shadow-[0px_4px_0px_0px_rgba(255,255,255,0.3)]",
        "hover:-translate-y-1",
      ],
      neubrutalism: [
        "border-[1px]",
        "border-black dark:border-white/70",
        "shadow-[3px_3px_0px_0px_rgba(0,0,0)]",
        "dark:shadow-[2px_2px_0px_0px_rgba(255,255,255,0.7)]",
        "hover:shadow-[5px_5px_0px_0px_rgba(0,0,0)]",
        "dark:hover:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.7)]",
        "hover:-translate-y-1 hover:-translate-x-1",
      ],
      corners: [
        "hover:shadow-md",
        "hover:-translate-y-1",
      ],
    },
  },
  defaultVariants: {
    variant: "gradient",
  },
});

export function PostCard({
  post,
  className,
  variant = "gradient",
}: {
  post: Post;
  className?: string;
  variant?: "default" | "gradient" | "lifted" | "neubrutalism" | "corners";
}) {
  // Convert timestamp to Switzerland time zone
  const zurichTime = React.useMemo(() => {
    try {
      return toZonedTime(new Date(post.timestamp), "Europe/Zurich");
    } catch {
      return new Date(post.timestamp);
    }
  }, [post.timestamp]);

  const formattedTime = React.useMemo(() => {
    try {
      return formatDistanceToNow(zurichTime, { addSuffix: true });
    } catch {
      return post.timestamp;
    }
  }, [zurichTime, post.timestamp]);

  const formattedDate = React.useMemo(() => {
    try {
      return format(zurichTime, "yyyy-MM-dd HH:mm");
    } catch {
      return post.timestamp;
    }
  }, [zurichTime, post.timestamp]);

  // Remove images, then sanitize and truncate HTML content
  const safeHtml = React.useMemo(() => {
    const noImages = removeImages(post.content);
    const truncated = truncateText(noImages, 1200);
    return DOMPurify.sanitize(truncated);
  }, [post.content]);

  return (
    <Card
      className={cn(
        postCardVariants({ variant }),
        "overflow-hidden border bg-card text-card-foreground",
        className
      )}
    >
      <div className="flex flex-col md:flex-row gap-2">
        {post.thumbnail && (
          <div className="md:w-1/4 overflow-hidden">
            <div className="h-full w-full relative aspect-video md:aspect-square">
              <img
                src={post.thumbnail}
                alt={post.title}
                className="object-cover h-full w-full rounded-t-lg md:rounded-l-lg md:rounded-t-none transition-transform duration-300 group-hover:scale-105"
              />
            </div>
          </div>
        )}

        <CardContent className={cn(
          "flex-1 p-3 md:p-4",
          post.thumbnail ? "md:w-3/4" : "w-full"
        )}>
          <div className="flex flex-col h-full">
            <div className="space-y-2 mb-2">
              <div className="flex items-center justify-between gap-2">
                <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20">
                  {post.source}
                </Badge>
                <div className="flex flex-col items-end text-muted-foreground text-xs gap-0.5">
                  <div className="flex items-center gap-1.5">
                    <Clock className="h-3 w-3" />
                    <span>{formattedTime}</span>
                  </div>
                  <span className="text-[11px] text-muted-foreground">{formattedDate} (CH)</span>
                </div>
              </div>

              <a
                href={post.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group/link"
              >
                <h3 className="font-semibold text-base md:text-lg leading-tight text-foreground group-hover/link:text-primary transition-colors duration-200">
                  {post.title || "Untitled"}
                  <ExternalLink className="inline-block ml-1.5 h-3.5 w-3.5 opacity-0 group-hover/link:opacity-100 transition-opacity" />
                </h3>
              </a>
            </div>

            <div className="text-sm text-muted-foreground mb-2 line-clamp-16 prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: safeHtml }} />

            <div className="mt-auto flex items-center text-xs text-muted-foreground">
              <Globe className="h-3 w-3 mr-1.5" />
              <span>{post.platform}</span>
            </div>
          </div>
        </CardContent>
      </div>
    </Card>
  );
}
