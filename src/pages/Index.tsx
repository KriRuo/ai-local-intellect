
import { Layout } from "@/components/Layout";
import { PostsFeed } from "@/components/PostsFeed";
import { ChatBox } from "@/components/ChatBox";
import { useIsMobile } from "@/hooks/use-mobile";
import { Tab, TabContent, TabList, TabTrigger, Tabs } from "@/components/ui/tabs";
import { useState } from "react";
import { MessageSquare, Newspaper } from "lucide-react";

const Index = () => {
  const isMobile = useIsMobile();
  const [activeTab, setActiveTab] = useState<string>("posts");

  if (isMobile) {
    return (
      <Layout>
        <Tabs
          defaultValue="posts"
          className="w-full"
          onValueChange={setActiveTab}
          value={activeTab}
        >
          <TabList className="grid grid-cols-2 mb-4">
            <TabTrigger value="posts" className="flex items-center gap-2">
              <Newspaper className="h-4 w-4" />
              <span>News</span>
            </TabTrigger>
            <TabTrigger value="chat" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              <span>Assistant</span>
            </TabTrigger>
          </TabList>
          <TabContent value="posts" className="space-y-4">
            <PostsFeed />
          </TabContent>
          <TabContent value="chat" className="h-[70vh]">
            <ChatBox />
          </TabContent>
        </Tabs>
      </Layout>
    );
  }

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
