import { ContentList } from '@/components/ContentList';
import { useNavigation } from '@/contexts/NavigationContext';

/**
 * Index page is the main entry point of the application
 * 
 * Features:
 * 1. Responsive layout with sidebar navigation
 * 2. Content sections for Dashboard, RSS Feeds, and Web Scraped content
 * 3. Dynamic content loading based on selected section
 */
const Index = () => {
  const { activeSection } = useNavigation();

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return (
          <div className="text-muted-foreground">
            <h2 className="text-xl font-semibold mb-4">Cool AI & Research Links</h2>
            <ul className="list-disc list-inside space-y-2">
              <li><a href="https://ai.ethz.ch/research/publications.html" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">ETH Zurich AI Publications</a></li>
              <li><a href="https://haystack.deepset.ai/blog" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Haystack Blog</a></li>
              <li><a href="https://syncedreview.com/category/popular/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Synced Popular</a></li>
              <li><a href="https://venturebeat.com/category/ai/page/2/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">VentureBeat AI</a></li>
              <li><a href="https://the-decoder.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">The Decoder</a></li>
              <li><a href="https://newsroom.ibm.com/latest-news-artificial-intelligence?l=100" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">IBM AI Newsroom</a></li>
              <li><a href="https://research.ibm.com/blog" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">IBM Research Blog</a></li>
              <li><a href="https://research.ibm.com/publications" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">IBM Research Publications</a></li>
              <li><a href="https://cohere.com/blog" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Cohere Blog</a></li>
              <li><a href="https://www.perplexity.ai/hub" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Perplexity Hub</a></li>
              <li><a href="https://x.ai/news" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">xAI News</a></li>
              <li><a href="https://ai.meta.com/blog/?page=1" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Meta AI Blog</a></li>
            </ul>
          </div>
        );
      case 'rss':
        return (
          <div className="space-y-8">
            <section>
              <h2 className="text-xl font-semibold mb-4">Analytics Vidhya</h2>
              <ContentList
                type="rss"
                url="https://www.analyticsvidhya.com/feed/"
                source="Analytics Vidhya"
                platform="Blog"
              />
            </section>
          </div>
        );
      case 'ws':
        return <ContentList type="ws" />;
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">
        {activeSection === 'dashboard' && 'Dashboard'}
        {activeSection === 'rss' && 'RSS Feeds'}
        {activeSection === 'ws' && 'Web Scraped Content'}
      </h1>
      {renderContent()}
    </div>
  );
};

export default Index;
