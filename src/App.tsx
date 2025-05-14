import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { ThemeProvider } from "@/hooks/use-theme";
import { NavigationProvider } from "@/contexts/NavigationContext";
import { Layout } from "./components/Layout";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import RssFeed from "./pages/RssFeed";
import RssSources from "./pages/RssSources";
import RssRuns from "./pages/RssRuns";
import Preferences from "./pages/Preferences";
import WebFeed from "./pages/WebFeed";
import SavedContent from "./pages/SavedContent";
import Dashboard from "./pages/Dashboard";

/**
 * Application root component
 * 
 * Provides:
 * 1. Global providers for UI components (theme, tooltips, toasts)
 * 2. React Query client for potential future data fetching needs
 * 3. Routing configuration with React Router
 * 4. Navigation state management
 * 5. Layout wrapper for consistent UI structure
 */
const queryClient = new QueryClient();

const App = () => (
  <ThemeProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <NavigationProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/rss-feed" element={<RssFeed />} />
                <Route path="/web-feed" element={<WebFeed />} />
                <Route path="/rss-sources" element={<RssSources />} />
                <Route path="/rss-runs" element={<RssRuns />} />
                <Route path="/preferences" element={<Preferences />} />
                <Route path="/saved" element={<SavedContent />} />
                {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Layout>
          </BrowserRouter>
        </NavigationProvider>
      </TooltipProvider>
    </QueryClientProvider>
  </ThemeProvider>
);

export default App;
