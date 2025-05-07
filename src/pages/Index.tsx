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
            Dashboard content coming soon...
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
