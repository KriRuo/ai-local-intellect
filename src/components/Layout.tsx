
import { ThemeToggle } from "./ThemeToggle";
import { Brain } from "lucide-react";

/**
 * Layout component provides the main structure of the application
 * 
 * Features:
 * 1. Sticky header with app branding and theme toggle
 * 2. Main content area with container width
 * 3. Footer with application information
 * 4. Apple-inspired styling with light background and subtle shadows
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
          <ThemeToggle />
        </div>
      </header>
      <main className="flex-1 container py-8">
        {children}
      </main>
      <footer className="border-t border-gray-100 py-6 bg-white/80">
        <div className="container text-center text-sm text-muted-foreground">
          AI Insight Tracker - A local-first AI news aggregator
        </div>
      </footer>
    </div>
  );
}
