import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Search, Bell } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { useApi } from "@/hooks/useApi";
import { useTheme } from "@/hooks/useTheme";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const navigate = useNavigate();
  const { theme, toggle } = useTheme();
  const { data: alertsData } = useApi(() => api.alerts.list(), []);
  const unreadAlerts = (alertsData ?? []).filter((a) => !a.read).length;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/markets?q=${encodeURIComponent(searchQuery)}`);
      setSearchOpen(false);
    }
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AppSidebar theme={theme} toggleTheme={toggle} />
        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-14 flex items-center justify-between border-b border-border px-4 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
            <div className="flex items-center gap-3">
              <SidebarTrigger />
              <form onSubmit={handleSearch} className="hidden sm:flex items-center">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search stocks, signals..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 pr-4 py-1.5 text-sm bg-secondary rounded-lg border-none outline-none focus:ring-2 focus:ring-primary/30 w-64 text-foreground placeholder:text-muted-foreground"
                  />
                </div>
              </form>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSearchOpen(!searchOpen)}
                className="sm:hidden p-2 rounded-lg hover:bg-accent text-muted-foreground"
              >
                <Search className="h-5 w-5" />
              </button>
              <button
                onClick={() => navigate("/alerts")}
                className="relative p-2 rounded-lg hover:bg-accent text-muted-foreground transition-colors"
              >
                <Bell className="h-5 w-5" />
                {unreadAlerts > 0 && (
                  <span className="absolute top-1 right-1 h-4 w-4 rounded-full bg-bearish text-[10px] text-primary-foreground flex items-center justify-center font-medium">
                    {unreadAlerts}
                  </span>
                )}
              </button>
            </div>
          </header>

          {searchOpen && (
            <div className="sm:hidden p-3 border-b border-border bg-card">
              <form onSubmit={handleSearch} className="flex items-center">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search stocks, signals..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 pr-4 py-2 text-sm bg-secondary rounded-lg border-none outline-none focus:ring-2 focus:ring-primary/30 w-full text-foreground placeholder:text-muted-foreground"
                    autoFocus
                  />
                </div>
              </form>
            </div>
          )}

          <main className="flex-1 p-4 md:p-6 overflow-auto">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  );
}
