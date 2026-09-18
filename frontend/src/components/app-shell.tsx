import { Link, useRouterState } from "@tanstack/react-router";
import {
  Activity,
  Bell,
  ChartNoAxesCombined,
  CircleUserRound,
  FileCheck2,
  FileText,
  Gauge,
  RefreshCw,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
} from "lucide-react";
import { useMemo, type ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { useAuth } from "@/lib/auth/auth-context";
import { canAccessRoute } from "@/lib/auth/rbac-permissions";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import { ProfileMenu } from "@/components/profile-menu";

type NavItem = {
  title: string;
  to:
    | "/"
    | "/contracts"
    | "/obligations"
    | "/renewals"
    | "/compliance"
    | "/reports"
    | "/notifications"
    | "/activity-logs"
    | "/users"
    | "/profile"
    | "/settings";
  icon: LucideIcon;
  badge?: string;
};

const workspaceItems: NavItem[] = [
  { title: "Dashboard", to: "/", icon: Gauge, badge: "4" },
  { title: "Contracts", to: "/contracts", icon: FileText },
  { title: "Obligations", to: "/obligations", icon: FileCheck2 },
  { title: "Renewals", to: "/renewals", icon: RefreshCw },
  { title: "Compliance", to: "/compliance", icon: ShieldCheck },
  { title: "Reports", to: "/reports", icon: ChartNoAxesCombined },
];

const systemItems: NavItem[] = [
  { title: "Notifications", to: "/notifications", icon: Bell, badge: "12" },
  { title: "Activity Logs", to: "/activity-logs", icon: Activity },
  { title: "Users", to: "/users", icon: SlidersHorizontal },
  { title: "Profile", to: "/profile", icon: CircleUserRound },
  { title: "Settings", to: "/settings", icon: Settings },
];

function LedgerSidebar() {
  const { user } = useAuth();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const { state } = useSidebar();
  const collapsed = state === "collapsed";

  const visibleWorkspaceItems = useMemo(
    () => workspaceItems.filter((item) => canAccessRoute(item.to, user?.role)),
    [user?.role],
  );

  const visibleSystemItems = useMemo(
    () => systemItems.filter((item) => canAccessRoute(item.to, user?.role)),
    [user?.role],
  );

  const renderItems = (items: NavItem[]) =>
    items.map((item) => (
      <SidebarMenuItem key={item.to}>
        <SidebarMenuButton asChild isActive={pathname === item.to} tooltip={item.title}>
          <Link to={item.to}>
            <item.icon />
            <span>{item.title}</span>
          </Link>
        </SidebarMenuButton>
        {item.badge && !collapsed ? <SidebarMenuBadge>{item.badge}</SidebarMenuBadge> : null}
      </SidebarMenuItem>
    ));

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-3 py-4">
        <Link to="/" className="flex items-center gap-2.5 overflow-hidden px-1">
          <span className="grid size-8 shrink-0 place-items-center rounded-md bg-sidebar-primary font-display text-sm font-semibold text-sidebar-primary-foreground">
            V
          </span>
          <span className="min-w-0 leading-tight group-data-[collapsible=icon]:hidden">
            <span className="block truncate font-display text-sm font-semibold text-sidebar-foreground">
              Vantage Ledger
            </span>
            <span className="block text-[10px] uppercase tracking-[0.18em] text-sidebar-foreground/40">
              CLM Console
            </span>
          </span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Workspace</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>{renderItems(visibleWorkspaceItems)}</SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>System</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>{renderItems(visibleSystemItems)}</SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="p-3">
        <div className="rounded-md border border-sidebar-border px-3 py-2.5 group-data-[collapsible=icon]:hidden">
          <p className="font-display text-[11px] font-semibold text-sidebar-foreground">
            All systems nominal
          </p>
          <p className="text-[11px] text-sidebar-foreground/40">Last sync 08:42 UTC</p>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <SidebarProvider>
      <LedgerSidebar />
      <div className="min-w-0 flex-1 bg-background">
        <header className="sticky top-0 z-20 flex h-14 items-center border-b border-border/70 bg-background/90 px-4 backdrop-blur-md">
          <SidebarTrigger aria-label="Collapse navigation" />
          <div className="ml-auto flex items-center gap-3">
            <ProfileMenu />
          </div>
        </header>
        {children}
      </div>
    </SidebarProvider>
  );
}
