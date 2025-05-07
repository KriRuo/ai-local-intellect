
import { Layout } from "@/components/Layout";
import { PostsFeed } from "@/components/PostsFeed";
import { ChatBox } from "@/components/ChatBox";
import { useIsMobile } from "@/hooks/use-mobile";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { MessageSquare, Newspaper } from "lucide-react";

/**
 * Index page is the main entry point of the application
 * 
 * Features:
 * 1. Responsive layout - different UIs for mobile and desktop
 * 2. Mobile: Tab-based navigation between news feed and AI assistant
 * 3. Desktop: Side-by-side display of news feed and AI assistant
 */
const Index = () => {
  // Detect if user is on a mobile device for responsive layout
  const isMobile = useIsMobile();
  const [activeTab, setActiveTab] = useState<string>("posts");

  // Mobile-specific layout with tabs
  if (isMobile) {
    return (
      <Layout>
        <Tabs
          defaultValue="posts"
          className="w-full"
          onValueChange={setActiveTab}
          value={activeTab}
        >
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="posts" className="flex items-center gap-2">
              <Newspaper className="h-4 w-4" />
              <span>News</span>
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              <span>Assistant</span>
            </TabsTrigger>
          </TabsList>
          <TabsContent value="posts" className="space-y-4">
            <PostsFeed />
          </TabsContent>
          <TabsContent value="chat" className="h-[70vh]">
            <ChatBox />
          </TabsContent>
        </Tabs>
      </Layout>
    );
  }

  // Desktop layout with grid
  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <Newspaper className="h-5 w-5" />
            Latest AI News & Insights
          </h2>
          <PostsFeed />
        </div>
        <div>
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            AI Assistant
          </h2>
          <div className="h-[calc(100vh-12rem)]">
            <ChatBox />
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Index;
