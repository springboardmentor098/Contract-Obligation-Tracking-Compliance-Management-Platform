import { useNavigate } from "@tanstack/react-router";
import { ArrowLeft, Home, LogOut, ShieldAlert } from "lucide-react";
import { useAuth } from "@/lib/auth/auth-context";
import { Button } from "@/components/ui/button";

export function AccessDenied({
  requiredRole,
  message,
}: {
  requiredRole?: string;
  message?: string;
}) {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();

  return (
    <main className="flex min-h-[70vh] flex-col items-center justify-center px-4 py-12 text-center">
      <div className="relative mx-auto flex size-20 items-center justify-center rounded-2xl bg-destructive/10 text-destructive shadow-sm ring-8 ring-destructive/5">
        <ShieldAlert className="size-10" />
      </div>

      <div className="mt-6 max-w-md space-y-2">
        <div className="inline-flex items-center gap-1.5 rounded-full border border-destructive/20 bg-destructive/5 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-destructive">
          Error 403 Forbidden
        </div>
        <h1 className="font-display text-3xl font-bold tracking-tight text-foreground">
          Access Denied
        </h1>
        <p className="text-sm text-muted-foreground">
          {message ||
            "You do not have the required permissions or role to view this page. If you believe this is in error, please contact your administrator."}
        </p>
      </div>

      <div className="mt-6 rounded-lg border border-border/80 bg-card p-4 text-left shadow-sm">
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-muted-foreground">Logged in as:</span>
            <p className="font-medium text-foreground">{user?.email || "Unknown"}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Your Role:</span>
            <p className="font-medium text-jade">{user?.role || "Unassigned"}</p>
          </div>
          {requiredRole ? (
            <div className="col-span-2 border-t border-border/60 pt-2">
              <span className="text-muted-foreground">Required Role:</span>
              <p className="font-medium text-foreground">{requiredRole}</p>
            </div>
          ) : null}
        </div>
      </div>

      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Button
          variant="outline"
          className="gap-2"
          onClick={() => window.history.back()}
        >
          <ArrowLeft className="size-4" />
          Go Back
        </Button>
        <Button
          className="gap-2 bg-jade text-primary-foreground hover:bg-jade/90"
          onClick={() => navigate({ to: "/" })}
        >
          <Home className="size-4" />
          Return to Dashboard
        </Button>
        <Button
          variant="ghost"
          className="gap-2 text-muted-foreground hover:text-destructive"
          onClick={() => signOut()}
        >
          <LogOut className="size-4" />
          Sign in as another user
        </Button>
      </div>
    </main>
  );
}
