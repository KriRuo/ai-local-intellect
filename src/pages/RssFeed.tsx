import { useState } from "react";
import { PostsFeed } from '@/components/PostsFeed';
import { importRssFeed } from '@/lib/api';
import feeds from '../../rss_sources.json'; // Import the feeds list

const RssFeed = () => {
  const [loading, setLoading] = useState(false);
  const [importedCount, setImportedCount] = useState(0);

  const handleImportAll = async () => {
    setLoading(true);
    setImportedCount(0);
    for (const feed of feeds) {
      try {
        await importRssFeed(feed.url, feed.source, feed.platform || "RSS");
        setImportedCount((count) => count + 1);
      } catch (e) {
        // Optionally handle errors per feed
      }
    }
    setLoading(false);
    window.location.reload(); // Or trigger a posts refresh in a better way
  };

  const handleTriggerScrape = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/scrape/rss/trigger', { method: 'POST' });
      if (response.ok) {
        alert('Scraping triggered!');
      } else {
        alert('Failed to trigger scraping.');
      }
    } catch (e) {
      alert('Failed to trigger scraping.');
    }
    setLoading(false);
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">RSS Feeds</h1>
      <button
        onClick={handleImportAll}
        disabled={loading}
        className="mb-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? `Importing... (${importedCount}/${feeds.length})` : "Import All RSS Feeds"}
      </button>
      <button
        onClick={handleTriggerScrape}
        disabled={loading}
        className="mb-6 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
      >
        {loading ? "Triggering Scrape..." : "Trigger RSS Scraping"}
      </button>
      <PostsFeed />
    </div>
  );
};

export default RssFeed; 