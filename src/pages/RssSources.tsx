import * as React from "react";
import { ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface RSSSource {
  source: string;
  url: string;
  description?: string;
  category?: string;
  source_type?: string;
  platform?: string;
}

function RSSSourcesList({ sources }: { sources: RSSSource[] }) {
  // Group sources by category
  const groupedSources = React.useMemo(() => {
    const grouped: Record<string, RSSSource[]> = {};
    sources.forEach((source) => {
      const cat = source.category || "Other";
      if (!grouped[cat]) grouped[cat] = [];
      grouped[cat].push(source);
    });
    return grouped;
  }, [sources]);

  const categories = React.useMemo(() => Object.keys(groupedSources).sort(), [groupedSources]);

  return (
    <div className="container mx-auto py-6 space-y-8">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">RSS Sources</h1>
        <p className="text-muted-foreground">Browse and manage your RSS feed sources</p>
      </div>
      {categories.map((category) => (
        <div key={category} className="space-y-4">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-semibold tracking-tight">{category}</h2>
            <Badge variant="outline" className="ml-2">{groupedSources[category].length}</Badge>
          </div>
          <Separator className="my-2" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {groupedSources[category].map((source, idx) => (
              <SourceCard key={source.url + idx} source={source} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function SourceCard({ source }: { source: RSSSource }) {
  return (
    <Card className="h-full transition-all hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg font-medium">{source.source}</CardTitle>
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
            title="Open source RSS feed"
          >
            <ExternalLink className="h-5 w-5" />
          </a>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {source.description && (
          <p className="text-sm text-muted-foreground line-clamp-2">{source.description}</p>
        )}
        <div className="flex flex-wrap gap-2">
          {source.source_type && (
            <Badge variant="secondary" className="text-xs">{source.source_type}</Badge>
          )}
          {source.platform && (
            <Badge variant="secondary" className="text-xs">{source.platform}</Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

const RssSources = () => {
  const [sources, setSources] = React.useState<RSSSource[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchSources = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("/api/rss-sources");
        const data = await res.json();
        if (data.status === "success") {
          setSources(data.data);
        } else {
          setError("Failed to load RSS sources");
        }
      } catch (e) {
        setError("Failed to load RSS sources");
      }
      setLoading(false);
    };
    fetchSources();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading RSS sources...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center max-w-md">
          <h3 className="text-lg font-medium mb-2">Failed to load RSS sources</h3>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return <RSSSourcesList sources={sources} />;
};

export default RssSources; 