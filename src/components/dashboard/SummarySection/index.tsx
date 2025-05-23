import * as React from 'react';
import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { format } from 'date-fns';
import { CalendarIcon } from 'lucide-react';

const SummarySection: React.FC = () => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [availableSources, setAvailableSources] = useState<string[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<{ from: Date; to: Date }>({
    from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    to: new Date()
  });
  const [summary, setSummary] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetch('/api/rss-sources')
      .then(res => res.json())
      .then(data => {
        if (data && data.data) {
          setAvailableSources(data.data.map((feed: any) => feed.source));
        }
      });
  }, []);

  const handleSourceChange = (source: string, checked: boolean) => {
    if (source === "All") {
      setSelectedSources(checked ? ["All", ...availableSources] : []);
    } else {
      let newSelected = checked
        ? [...selectedSources.filter(s => s !== "All"), source]
        : selectedSources.filter(s => s !== source && s !== "All");
      if (newSelected.length === availableSources.length) {
        newSelected = ["All", ...availableSources];
      }
      setSelectedSources(newSelected);
    }
  };

  const sourcesToSend = selectedSources.includes("All")
    ? availableSources
    : selectedSources;

  const handleGenerateSummary = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/lm/summarize-articles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sources: sourcesToSend,
          start_date: format(dateRange.from, 'yyyy-MM-dd'),
          end_date: format(dateRange.to, 'yyyy-MM-dd'),
          combined: true
        })
      });
      const data = await response.json();
      console.log('Summary API Response:', data);
      if (data.error) {
        console.error('Summary generation error:', data.error);
        setSummary(`Error: ${data.error}`);
      } else if (data.summary) {
        setSummary(data.summary);
      } else {
        console.error('Unexpected response format:', data);
        setSummary('Error: Unexpected response format from server');
      }
    } catch (error) {
      let message = 'Unknown error';
      if (error instanceof Error) {
        message = error.message;
      } else if (typeof error === 'string') {
        message = error;
      }
      console.error('Summary generation failed:', error);
      setSummary(`Failed to generate summary: ${message}`);
    } finally {
      setIsLoading(false);
      setIsDialogOpen(false);
    }
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <Button onClick={() => setIsDialogOpen(true)}>
          Generate Summary
        </Button>
      </div>
      {isLoading ? (
        <div className="space-y-4">
          <div className="h-24 bg-muted rounded-md animate-pulse" />
          <div className="space-y-2">
            <div className="h-4 bg-muted rounded-md w-3/4 animate-pulse" />
            <div className="h-4 bg-muted rounded-md animate-pulse" />
            <div className="h-4 bg-muted rounded-md w-5/6 animate-pulse" />
          </div>
        </div>
      ) : summary ? (
        <div className="prose prose-sm max-w-none">
          <div 
            dangerouslySetInnerHTML={{ 
              __html: summary || 'No summary available' 
            }} 
          />
        </div>
      ) : (
        <div className="text-sm text-muted-foreground">
          Click "Generate Summary" to create a summary of recent news articles.
        </div>
      )}
      {/* Dialog for selecting sources and date range */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Generate Summary</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent scrollbar-thumb-rounded">
            <div>
              <h4 className="font-medium">Select Sources</h4>
              <div className="grid gap-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="All"
                    checked={selectedSources.includes("All")}
                    onCheckedChange={checked => handleSourceChange("All", Boolean(checked))}
                  />
                  <label htmlFor="All" className="text-sm font-medium">All</label>
                </div>
                {availableSources.map((source) => (
                  <div key={source} className="flex items-center space-x-2">
                    <Checkbox
                      id={source}
                      checked={selectedSources.includes(source) || selectedSources.includes("All")}
                      onCheckedChange={checked => handleSourceChange(source, Boolean(checked))}
                    />
                    <label htmlFor={source} className="text-sm font-medium">{source}</label>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium">Date Range</h4>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full justify-start text-left font-normal">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {dateRange.from ? (
                      dateRange.to ? (
                        <>
                          {format(dateRange.from, "LLL dd, y")} -{" "}
                          {format(dateRange.to, "LLL dd, y")}
                        </>
                      ) : (
                        format(dateRange.from, "LLL dd, y")
                      )
                    ) : (
                      <span>Pick a date range</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={dateRange.from}
                    selected={dateRange}
                    onSelect={(range: any) => setDateRange(range)}
                    numberOfMonths={2}
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleGenerateSummary} disabled={sourcesToSend.length === 0 || !dateRange.from || !dateRange.to}>
              Generate Summary
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
};

export default SummarySection; 