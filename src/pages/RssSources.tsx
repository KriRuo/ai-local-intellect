import * as React from "react";
import { ExternalLink, Pencil } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { API_BASE_URL } from "@/lib/api";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose, DialogDescription } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';

interface RSSSource {
  source: string;
  url: string;
  description?: string;
  category?: string;
  source_type?: string;
  platform?: string;
}

function RSSSourcesList({ sources, onEdit }: { sources: RSSSource[], onEdit: (source: RSSSource) => void }) {
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
    <>
      {categories.map((category) => (
        <div key={category} className="space-y-4">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-semibold tracking-tight">{category}</h2>
            <Badge variant="outline" className="ml-2">{groupedSources[category].length}</Badge>
          </div>
          <Separator className="my-2" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {groupedSources[category].map((source, idx) => (
              <SourceCard key={source.url + idx} source={source} onEdit={onEdit} />
            ))}
          </div>
        </div>
      ))}
    </>
  );
}

function SourceCard({ source, onEdit }: { source: RSSSource, onEdit: (source: RSSSource) => void }) {
  return (
    <Card className="h-full transition-all hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg font-medium">{source.source}</CardTitle>
          <div className="flex gap-2 items-center">
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground transition-colors"
              title="Open source RSS feed"
            >
              <ExternalLink className="h-5 w-5" />
            </a>
            <Button variant="ghost" size="icon" onClick={() => onEdit(source)} title="Edit source">
              <Pencil className="h-4 w-4" />
            </Button>
          </div>
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

const CATEGORY_OPTIONS = [
  'AI News', 'AI Research', 'Machine Learning', 'Deep Learning', 'NLP', 'Data Science', 'AI Ethics', 'AI Business', 'AI Community', 'AI Infrastructure', 'Robotics', 'Tech News', 'Other',
];
const SOURCE_TYPE_OPTIONS = [
  'Industry', 'Academic', 'Company Blog', 'Research Institute', 'Magazine', 'News Site', 'Community', 'Framework', 'Publication', 'Newsletter', 'Podcast', 'Educational', 'Blog', 'Journal', 'Other',
];

const BULK_IMPORT_PLACEHOLDER = `[
  {
    "source": "Example Blog",
    "url": "https://example.com/rss",
    "platform": "RSS",
    "category": "AI News",
    "description": "Example description",
    "source_type": "Industry"
  }
]`;

const RssSources = () => {
  const [sources, setSources] = React.useState<RSSSource[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [modalOpen, setModalOpen] = React.useState(false);
  const [modalMode, setModalMode] = React.useState<'add' | 'edit'>('add');
  const [addLoading, setAddLoading] = React.useState(false);
  const [addError, setAddError] = React.useState<string | null>(null);
  const [form, setForm] = React.useState({
    source: '',
    url: '',
    platform: 'RSS',
    category: '',
    description: '',
    source_type: '',
  });
  const [originalUrl, setOriginalUrl] = React.useState<string | null>(null);
  const [bulkOpen, setBulkOpen] = React.useState(false);
  const [bulkInput, setBulkInput] = React.useState('');
  const [bulkLoading, setBulkLoading] = React.useState(false);
  const [bulkError, setBulkError] = React.useState<string | null>(null);
  const [bulkResult, setBulkResult] = React.useState<null | {added: number, skipped: number, errors: any[]}>(null);

  const fetchSources = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/rss-sources`);
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
  }, []);

  React.useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const openAddModal = () => {
    setForm({ source: '', url: '', platform: 'RSS', category: '', description: '', source_type: '' });
    setModalMode('add');
    setAddError(null);
    setModalOpen(true);
    setOriginalUrl(null);
  };

  const openEditModal = (source: RSSSource) => {
    setForm({
      source: source.source || '',
      url: source.url || '',
      platform: source.platform || 'RSS',
      category: source.category || '',
      description: source.description || '',
      source_type: source.source_type || '',
    });
    setModalMode('edit');
    setAddError(null);
    setModalOpen(true);
    setOriginalUrl(source.url);
  };

  const handleModalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddLoading(true);
    setAddError(null);
    try {
      let res;
      if (modalMode === 'add') {
        res = await fetch(`${API_BASE_URL}/rss-sources`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...form, platform: form.platform || 'RSS' }),
        });
      } else if (modalMode === 'edit' && originalUrl) {
        res = await fetch(`${API_BASE_URL}/rss-sources/${encodeURIComponent(originalUrl)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...form, platform: form.platform || 'RSS' }),
        });
      }
      if (!res || !res.ok) {
        const data = await res?.json().catch(() => ({}));
        setAddError(data?.detail || 'Failed to save RSS source.');
        setAddLoading(false);
        return;
      }
      setModalOpen(false);
      setForm({ source: '', url: '', platform: 'RSS', category: '', description: '', source_type: '' });
      fetchSources();
    } catch (err) {
      setAddError('Failed to save RSS source.');
    }
    setAddLoading(false);
  };

  const openBulkModal = () => {
    setBulkInput('');
    setBulkError(null);
    setBulkResult(null);
    setBulkOpen(true);
  };

  const handleBulkImport = async (e: React.FormEvent) => {
    e.preventDefault();
    setBulkLoading(true);
    setBulkError(null);
    setBulkResult(null);
    let parsed;
    try {
      parsed = JSON.parse(bulkInput);
      if (!Array.isArray(parsed)) throw new Error('Input must be a JSON array.');
    } catch (err: any) {
      setBulkError('Invalid JSON: ' + err.message);
      setBulkLoading(false);
      return;
    }
    try {
      const res = await fetch(`${API_BASE_URL}/rss-sources/bulk-import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed),
      });
      const data = await res.json();
      if (!res.ok) {
        setBulkError(data.detail || 'Bulk import failed.');
        setBulkLoading(false);
        return;
      }
      setBulkResult({ added: data.added, skipped: data.skipped, errors: data.errors });
      fetchSources();
    } catch (err) {
      setBulkError('Bulk import failed.');
    }
    setBulkLoading(false);
  };

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

  return (
    <div className="container mx-auto py-6 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0 mb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">RSS Sources</h1>
          <p className="text-muted-foreground">Browse and manage your RSS feed sources</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={modalOpen} onOpenChange={setModalOpen}>
            <DialogTrigger asChild>
              <Button variant="default" onClick={openAddModal}>Add New</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{modalMode === 'add' ? 'Add New RSS Source' : 'Edit RSS Source'}</DialogTitle>
                <DialogDescription>
                  {modalMode === 'add'
                    ? 'Enter the details for the new RSS feed source. The URL will be validated before adding.'
                    : 'Update the details for this RSS feed source. The URL will be validated if changed.'}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleModalSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="source">Source Name</Label>
                  <Input id="source" name="source" value={form.source} onChange={handleFormChange} required autoFocus />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <Label htmlFor="url">RSS Feed URL</Label>
                    {modalMode === 'edit' && (
                      <span className="text-destructive text-xs font-semibold flex items-center gap-1">
                        <span className="text-lg leading-none">&#33;</span> {/* Exclamation mark */}
                        Unique identifier! Changing this may break editing.
                      </span>
                    )}
                  </div>
                  <Input id="url" name="url" value={form.url} onChange={handleFormChange} required type="url" />
                </div>
                <div>
                  <Label htmlFor="platform">Platform</Label>
                  <Input id="platform" name="platform" value={form.platform} onChange={handleFormChange} placeholder="RSS" />
                </div>
                <div>
                  <Label htmlFor="category">Category</Label>
                  <Select value={form.category} onValueChange={(v) => handleSelectChange('category', v)}>
                    <SelectTrigger id="category">
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {CATEGORY_OPTIONS.map((cat) => (
                        <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="source_type">Source Type</Label>
                  <Select value={form.source_type} onValueChange={(v) => handleSelectChange('source_type', v)}>
                    <SelectTrigger id="source_type">
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      {SOURCE_TYPE_OPTIONS.map((type) => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea id="description" name="description" value={form.description} onChange={handleFormChange} rows={2} />
                </div>
                {addError && <div className="text-destructive text-sm">{addError}</div>}
                <DialogFooter>
                  <Button type="submit" disabled={addLoading}>{addLoading ? (modalMode === 'add' ? 'Adding...' : 'Saving...') : (modalMode === 'add' ? 'Add Source' : 'Save Changes')}</Button>
                  <DialogClose asChild>
                    <Button type="button" variant="ghost">Cancel</Button>
                  </DialogClose>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
          <Dialog open={bulkOpen} onOpenChange={setBulkOpen}>
            <DialogTrigger asChild>
              <Button variant="secondary" onClick={openBulkModal}>Bulk Import</Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Bulk Import RSS Sources</DialogTitle>
                <DialogDescription>
                  Paste a JSON array of sources below. Each object must match the <code>rss_sources.json</code> format.<br />
                  <span className="font-semibold">Example:</span>
                  <pre className="bg-muted rounded p-2 mt-2 text-xs overflow-x-auto whitespace-pre-wrap">{BULK_IMPORT_PLACEHOLDER}</pre>
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleBulkImport} className="space-y-4">
                <div>
                  <Label htmlFor="bulk-input">Sources JSON</Label>
                  <Textarea
                    id="bulk-input"
                    name="bulk-input"
                    value={bulkInput}
                    onChange={e => setBulkInput(e.target.value)}
                    rows={10}
                    placeholder={BULK_IMPORT_PLACEHOLDER}
                    className="resize-y min-h-[120px] max-h-[400px] font-mono"
                  />
                </div>
                {bulkError && <div className="text-destructive text-sm">{bulkError}</div>}
                {bulkResult && (
                  <div className="text-sm space-y-1">
                    <div className="font-semibold">Import Summary:</div>
                    <div>Added: <span className="font-mono">{bulkResult.added}</span></div>
                    <div>Skipped (duplicates): <span className="font-mono">{bulkResult.skipped}</span></div>
                    {bulkResult.errors.length > 0 && (
                      <div className="text-destructive">Errors:
                        <ul className="list-disc ml-6">
                          {bulkResult.errors.map((err, i) => (
                            <li key={i} className="break-all">[{err.index}] {err.error}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
                <DialogFooter>
                  <Button type="submit" disabled={bulkLoading}>{bulkLoading ? 'Importing...' : 'Import'}</Button>
                  <DialogClose asChild>
                    <Button type="button" variant="ghost">Cancel</Button>
                  </DialogClose>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>
      <div>
        <RSSSourcesList sources={sources} onEdit={openEditModal} />
      </div>
    </div>
  );
};

export default RssSources; 