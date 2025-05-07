
import { ThemeToggle } from "./ThemeToggle";
import { Brain } from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="border-b border-gray-100 shadow-sm">
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
      <footer className="border-t border-gray-100 py-6">
        <div className="container text-center text-sm text-muted-foreground">
          AI Insight Tracker - A local-first AI news aggregator
        </div>
      </footer>
    </div>
  );
}
