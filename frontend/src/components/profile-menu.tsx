import { useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import {
  Activity,
  ChevronDown,
  Loader2,
  LogOut,
  Settings,
  Shield,
  User,
} from "lucide-react";
import { toast } from "sonner";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth/auth-context";

import { canAccessRoute } from "@/lib/auth/rbac-permissions";

export function ProfileMenu() {
  const { user, signOut } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const navigate = useNavigate();

  // Compute display initials from user name or email
  const displayName = user?.name || user?.email?.split("@")[0] || "User";
  const initials = displayName
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const handleLogout = async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);
    try {
      await signOut();
      toast.success("Logged out successfully");
    } catch (error) {
      console.error("Logout error:", error);
      // Graceful degradation: still navigate to login
      toast.info("Session ended");
      navigate({ to: "/login", replace: true });
    } finally {
      setIsLoggingOut(false);
    }
  };

  const showActivities = canAccessRoute("/activity-logs", user?.role);
  const showSettings = canAccessRoute("/settings", user?.role);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label="User profile menu"
          className="group flex items-center gap-2 rounded-full p-1 transition-colors hover:bg-secondary/80 focus:outline-none focus:ring-2 focus:ring-jade/40 sm:rounded-md sm:px-2.5 sm:py-1.5"
        >
          {/* Avatar image or circle */}
          {user?.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={displayName}
              className="size-8 shrink-0 rounded-full object-cover ring-1 ring-jade/20 transition-transform group-hover:scale-105"
            />
          ) : (
            <span className="grid size-8 shrink-0 place-items-center rounded-full bg-jade/10 font-display text-xs font-semibold text-jade ring-1 ring-jade/20 transition-transform group-hover:scale-105">
              {initials}
            </span>
          )}

          {/* User metadata on sm+ screens */}
          <div className="hidden text-left sm:block">
            <span className="block max-w-[140px] truncate text-xs font-medium text-foreground">
              {displayName}
            </span>
            <span className="block text-[10px] text-muted-foreground">
              {user?.role || "Viewer"}
            </span>
          </div>

          <ChevronDown className="hidden size-3.5 text-muted-foreground/70 transition-transform group-data-[state=open]:rotate-180 sm:block" />
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent className="w-56" align="end" sideOffset={8}>
        {/* Profile Card Header */}
        <DropdownMenuLabel className="font-normal p-2.5">
          <div className="flex flex-col space-y-1">
            <div className="flex items-center justify-between gap-2">
              <p className="truncate text-sm font-semibold leading-none">{displayName}</p>
              {user?.role && (
                <Badge variant="outline" className="border-jade/30 text-[10px] text-jade px-1.5 py-0">
                  {user.role}
                </Badge>
              )}
            </div>
            <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
          </div>
        </DropdownMenuLabel>

        <DropdownMenuSeparator />

        {/* Quick Links */}
        <DropdownMenuGroup>
          <DropdownMenuItem asChild>
            <Link to="/profile" className="flex w-full cursor-pointer items-center gap-2 text-xs">
              <User className="size-4 text-muted-foreground" />
              <span>My Profile</span>
            </Link>
          </DropdownMenuItem>
          {showActivities ? (
            <DropdownMenuItem asChild>
              <Link to="/activity-logs" className="flex w-full cursor-pointer items-center gap-2 text-xs">
                <Activity className="size-4 text-muted-foreground" />
                <span>Activity Logs</span>
              </Link>
            </DropdownMenuItem>
          ) : null}
          {showSettings ? (
            <DropdownMenuItem asChild>
              <Link to="/settings" className="flex w-full cursor-pointer items-center gap-2 text-xs">
                <Settings className="size-4 text-muted-foreground" />
                <span>Workspace Settings</span>
              </Link>
            </DropdownMenuItem>
          ) : null}
        </DropdownMenuGroup>

        <DropdownMenuSeparator />

        {/* Secure Logout Action */}
        <DropdownMenuItem
          onClick={handleLogout}
          disabled={isLoggingOut}
          className="cursor-pointer gap-2 text-xs text-destructive focus:bg-destructive/10 focus:text-destructive"
        >
          {isLoggingOut ? (
            <>
              <Loader2 className="size-4 animate-spin text-destructive" />
              <span>Signing out…</span>
            </>
          ) : (
            <>
              <LogOut className="size-4" />
              <span>Log Out</span>
            </>
          )}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
