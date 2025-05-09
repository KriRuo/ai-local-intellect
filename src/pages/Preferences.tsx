import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const CATEGORY_OPTIONS = [
  "Artificial General Intelligence (AGI)",
  "Large Language Models (LLMs)",
  "Natural Language Processing (NLP)",
  "Computer Vision",
  "Reinforcement Learning",
  "Robotics",
  "AI Ethics & Safety",
  "AI Research",
  "AI Applications (e.g. healthcare, finance, education)",
  "AI Infrastructure & Tooling (e.g. GPUs, frameworks, APIs)",
  "AI Policy & Regulation",
  "AI Startups & Business",
  "Multimodal AI",
  "Open-Source AI",
  "Other"
];

export default function Preferences() {
  const [sources, setSources] = useState<{ source: string }[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log("Preferences page mounted");
    async function fetchData() {
      setLoading(true);
      try {
        const [sourcesRes, prefsRes] = await Promise.all([
          fetch("/api/rss-sources", { cache: "no-store" }),
          fetch("/api/preferences")
        ]);
        const sourcesData = await sourcesRes.json();
        console.log("sourcesData", sourcesData);
        setSources(sourcesData.data || []);
        const prefsData = await prefsRes.json();
        setSelectedSources(prefsData.preferred_sources || []);
        setSelectedCategories(prefsData.preferred_categories || []);
      } catch (e) {
        setError("Failed to load preferences or sources.");
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  const handleSourceToggle = (source: string) => {
    setSelectedSources((prev) =>
      prev.includes(source) ? prev.filter((s) => s !== source) : [...prev, source]
    );
  };

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category) ? prev.filter((c) => c !== category) : [...prev, category]
    );
  };

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const res = await fetch("/api/preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          preferred_sources: selectedSources,
          preferred_categories: selectedCategories
        })
      });
      if (!res.ok) throw new Error("Failed to save preferences");
      setSaved(true);
    } catch (e) {
      setError("Failed to save preferences.");
    }
    setSaving(false);
  };

  if (loading) {
    return <div className="flex justify-center items-center min-h-[400px]">Loading preferences...</div>;
  }

  return (
    <div className="container mx-auto py-8 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Your Preferences</CardTitle>
          <p className="text-muted-foreground mt-2">Select your favorite sources and categories. News from these will be ranked higher for you.</p>
        </CardHeader>
        <CardContent>
          {error && <div className="text-red-500 mb-4">{error}</div>}
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Preferred Sources</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {sources.map((src) => (
                <label key={src.source} className="flex items-center gap-2 cursor-pointer">
                  <Checkbox
                    checked={selectedSources.includes(src.source)}
                    onCheckedChange={() => handleSourceToggle(src.source)}
                  />
                  <span>{src.source}</span>
                </label>
              ))}
            </div>
            {selectedSources.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {selectedSources.map((src) => (
                  <Badge key={src}>{src}</Badge>
                ))}
              </div>
            )}
          </div>
          <Separator className="my-4" />
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Preferred Categories</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {CATEGORY_OPTIONS.map((cat) => (
                <label key={cat} className="flex items-center gap-2 cursor-pointer">
                  <Checkbox
                    checked={selectedCategories.includes(cat)}
                    onCheckedChange={() => handleCategoryToggle(cat)}
                  />
                  <span>{cat}</span>
                </label>
              ))}
            </div>
            {selectedCategories.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {selectedCategories.map((cat) => (
                  <Badge key={cat}>{cat}</Badge>
                ))}
              </div>
            )}
          </div>
          <Button onClick={handleSave} disabled={saving} className="mt-4 w-full">
            {saving ? "Saving..." : "Save Preferences"}
          </Button>
          {saved && <div className="text-green-600 mt-2">Preferences saved!</div>}
        </CardContent>
      </Card>
    </div>
  );
} 