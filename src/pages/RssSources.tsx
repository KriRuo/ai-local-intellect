import { useEffect, useState } from "react";

interface RssSource {
  url: string;
  source: string;
  platform?: string;
}

const RssSources = () => {
  const [sources, setSources] = useState<RssSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
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

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">RSS Sources</h1>
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && (
        <ul className="space-y-4">
          {sources.map((src, idx) => (
            <li key={idx} className="border rounded p-4 bg-white shadow">
              <div className="font-semibold">{src.source}</div>
              <div className="text-sm text-gray-600">{src.url}</div>
              <div className="text-xs text-gray-400">{src.platform || "RSS"}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default RssSources; 