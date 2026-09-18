import { useNavigate, useRouterState } from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";
import { useAuth } from "@/lib/auth/auth-context";
import { canAccessRoute } from "@/lib/auth/rbac-permissions";
import { AccessDenied } from "@/components/access-denied";

const PUBLIC_ROUTES = ["/login", "/forgot-password", "/reset-password"];

export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, isHydrated, user } = useAuth();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const navigate = useNavigate();
  const isPublic = PUBLIC_ROUTES.includes(pathname);

  useEffect(() => {
    if (isHydrated && !isAuthenticated && !isPublic) {
      navigate({ to: "/login", replace: true });
    }
  }, [isHydrated, isAuthenticated, isPublic, navigate]);

  if (isPublic) return <>{children}</>;
  if (!isHydrated || !isAuthenticated) {
    return <div className="min-h-svh bg-background" aria-busy="true" />;
  }

  // Check RBAC route authorization
  if (!canAccessRoute(pathname, user?.role)) {
    return <AccessDenied />;
  }

  return <>{children}</>;
}

export function useIsPublicRoute() {
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  return PUBLIC_ROUTES.includes(pathname);
}
