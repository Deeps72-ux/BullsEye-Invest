import { LayoutDashboard, TrendingUp, Radar, Briefcase, Bell, MessageSquare, LogIn, Sun, Moon, Search, X } from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation } from "react-router-dom";
import {
  Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarGroupLabel,
  SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarFooter, useSidebar,
} from "@/components/ui/sidebar";

const mainItems = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Markets", url: "/markets", icon: TrendingUp },
  { title: "Signals", url: "/signals", icon: Radar },
  { title: "Portfolio", url: "/portfolio", icon: Briefcase },
  { title: "Alerts", url: "/alerts", icon: Bell },
  { title: "AI Chat", url: "/chat", icon: MessageSquare },
];

interface AppSidebarProps {
  theme: "light" | "dark";
  toggleTheme: () => void;
}

export function AppSidebar({ theme, toggleTheme }: AppSidebarProps) {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();

  return (
    <Sidebar collapsible="icon" className="border-r border-border">
      <SidebarContent>
        <div className={`p-4 ${collapsed ? "px-2" : ""}`}>
          <div className="flex items-center gap-2">
            <img src="/bullseye.png" alt="BullsEye" className="h-8 w-8 rounded-lg object-contain flex-shrink-0" />
            {!collapsed && <span className="font-heading font-bold text-lg text-foreground">BullsEye</span>}
          </div>
        </div>

        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      end={item.url === "/"}
                      className="hover:bg-accent/50 transition-colors"
                      activeClassName="bg-primary/10 text-primary font-medium"
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-3">
        <button
          onClick={toggleTheme}
          className="flex items-center gap-2 w-full p-2 rounded-lg hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          {!collapsed && <span className="text-sm">{theme === "dark" ? "Light Mode" : "Dark Mode"}</span>}
        </button>
        <SidebarMenuButton asChild>
          <NavLink to="/login" className="hover:bg-accent/50" activeClassName="bg-primary/10 text-primary">
            <LogIn className="mr-2 h-4 w-4" />
            {!collapsed && <span>Login</span>}
          </NavLink>
        </SidebarMenuButton>
      </SidebarFooter>
    </Sidebar>
  );
}
