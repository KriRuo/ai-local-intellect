import { ThemeToggle } from "./ThemeToggle";
import { Brain } from "lucide-react";
import { IndustrialSidebar } from "./IndustrialSidebar";
import { BackendStatusLight } from "./BackendStatusLight";

/**
 * Layout component provides the main structure of the application.
 *
 * - Sticky header with app branding and theme toggle
 * - Sidebar navigation with collapsible sections
 * - Main content area with container width
 * - Footer with backend status and addresses
 *
 * @param children - React children to render in the main content area
 */
interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-medium">AI Insight Tracker</h1>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        <IndustrialSidebar />
        <main className="flex-1 container py-8 ml-[3.05rem]">
          {children}
        </main>
      </div>
      <footer className="border-t border-gray-100 py-6 bg-white/80">
        <div className="container text-center text-sm text-muted-foreground">
          <div>AI Insight Tracker - A local-first AI news aggregator</div>
          <div className="mt-2 flex items-center justify-center gap-2">
            <BackendStatusLight />
            <span>Backend: {import.meta.env.VITE_API_URL}</span>
            <span>Local address: {window.location.origin}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
