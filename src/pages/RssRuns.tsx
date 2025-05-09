import * as React from "react";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { API_BASE_URL } from "@/lib/api";

interface RssRun {
  id: number;
  started_at: string;
  ended_at: string | null;
  duration_seconds: number | null;
  num_sources_total: number;
  num_sources_skipped: number;
  num_sources_captured: number;
  num_articles_captured: number;
  status: string;
  error_message?: string | null;
}

const statusIcon = (status: string) => {
  if (status === "completed") return <CheckCircle className="text-green-600" />;
  if (status === "failed") return <XCircle className="text-red-600" />;
  return <Loader2 className="animate-spin text-yellow-500" />;
};

function formatDuration(seconds: number | null) {
  if (seconds == null) return "-";
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${mins}m ${secs}s`;
}

const RssRuns: React.FC = () => {
  const [runs, setRuns] = React.useState<RssRun[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchRuns = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE_URL}/rss-runs`);
        const data = await res.json();
        if (data.status === "success") {
          setRuns(data.data);
        } else {
          setError("Failed to load RSS runs");
        }
      } catch (e) {
        setError("Failed to load RSS runs");
      }
      setLoading(false);
    };
    fetchRuns();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading RSS runs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center max-w-md">
          <h3 className="text-lg font-medium mb-2">Failed to load RSS runs</h3>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-8">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">RSS Scraping Runs</h1>
        <p className="text-muted-foreground">History of all RSS scraping runs and their results</p>
      </div>
      <Separator className="my-2" />
      <div
        className="flex flex-col gap-4 max-h-[70vh] overflow-y-auto pr-2"
        style={{ scrollbarGutter: 'stable' }}
      >
        {[...runs].sort((a, b) => b.id - a.id).map((run) => (
          <Card key={run.id} className="w-full transition-all hover:shadow-md">
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
              <CardTitle className="text-lg font-medium flex items-center gap-2">
                {statusIcon(run.status)}
                Run #{run.id}
              </CardTitle>
              <span className="text-xs text-muted-foreground">
                {new Date(run.started_at).toLocaleString()}
              </span>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">{run.status}</Badge>
                {run.ended_at && (
                  <Badge variant="outline">Duration: {formatDuration(run.duration_seconds)}</Badge>
                )}
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm mt-2 max-w-xl">
                <div>Total sources:</div>
                <div className="font-semibold">{run.num_sources_total}</div>
                <div>Sources captured:</div>
                <div className="font-semibold">{run.num_sources_captured}</div>
                <div>Sources skipped:</div>
                <div className="font-semibold">{run.num_sources_skipped}</div>
                <div>Articles captured:</div>
                <div className="font-semibold">{run.num_articles_captured}</div>
              </div>
              {run.status === "failed" && run.error_message && (
                <div className="text-xs text-red-600 mt-2">Error: {run.error_message}</div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default RssRuns; 