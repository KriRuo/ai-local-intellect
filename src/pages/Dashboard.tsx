import { useEffect, useState } from "react";
import { NewsSection } from '@/components/dashboard/NewsSection/index';
import SummarySection from '@/components/dashboard/SummarySection';
import PersonalizedContentSection from '@/components/dashboard/PersonalizedSection/index';
import SavedSection from '@/components/dashboard/SavedSection';
import { SavedPost } from '@/components/dashboard/types';

// Main Dashboard component
export default function Dashboard() {
  // Saved posts state
  const [saved, setSaved] = useState<SavedPost[]>([]);
  const [loadingSaved, setLoadingSaved] = useState(true);
  // News state is now handled in NewsSection
  // User preferences state
  const [preferredSources, setPreferredSources] = useState<string[]>([]);
  const [preferredTopics, setPreferredTopics] = useState<string[]>([]);
  const [loadingPrefs, setLoadingPrefs] = useState(true);
  // const [newsVisibleCount, setNewsVisibleCount] = useState(10);

  useEffect(() => {
    // Fetch saved posts
    fetch("/api/saved")
      .then((res) => res.json())
      .then(setSaved)
      .finally(() => setLoadingSaved(false));
    // Fetch user preferences
    fetch("/api/preferences")
      .then((res) => res.json())
      .then((prefs) => {
        setPreferredSources(prefs.preferred_sources || []);
        setPreferredTopics(prefs.preferred_categories || []);
      })
      .finally(() => setLoadingPrefs(false));
  }, []);

  return (
    <div className="container mx-auto py-6 space-y-8">
      {/* News Section (moved to top) */}
      <NewsSection />

      {/* Personalized Content Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">Personalized Content</h2>
        </div>
        {loadingPrefs ? (
          <div>Loading...</div>
        ) : saved.length === 0 ? (
          <div className="text-muted-foreground">No personalized posts found.</div>
        ) : (
          <PersonalizedContentSection
            posts={saved.map((item) => item.post)}
            preferredTopics={preferredTopics}
            preferredSources={preferredSources}
          />
        )}
      </section>

      {/* Saved Content Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">Saved Content</h2>
        </div>
        <SavedSection saved={saved} loadingSaved={loadingSaved} />
      </section>

      {/* Summary Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">Summary</h2>
        </div>
        <SummarySection />
      </section>
    </div>
  );
} 