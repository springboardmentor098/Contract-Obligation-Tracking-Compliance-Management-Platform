import { createFileRoute, Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { AuthLayout } from "@/components/auth/auth-layout";
import { Field, FormMessage } from "@/components/auth/field";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth/auth-context";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign in | ContractIQ" },
      {
        name: "description",
        content: "Sign in to the ContractIQ enterprise contract intelligence workspace.",
      },
      { property: "og:title", content: "Sign in | ContractIQ" },
      {
        property: "og:description",
        content: "Sign in to the ContractIQ enterprise contract intelligence workspace.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const { signIn, isAuthenticated, isHydrated } = useAuth();
  const navigate = useNavigate();
  const expired = useRouterState({
    select: (state) => state.location.search as { expired?: string },
  }).expired;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [status, setStatus] = useState<"idle" | "loading" | "success">("idle");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isHydrated && isAuthenticated) navigate({ to: "/", replace: true });
  }, [isHydrated, isAuthenticated, navigate]);

  useEffect(() => {
    if (expired) navigate({ to: "/login", search: {}, replace: true });
  }, [expired, navigate]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (!email.trim()) {
      setError("Please enter your work email.");
      return;
    }
    if (!password) {
      setError("Please enter your password.");
      return;
    }
    setStatus("loading");
    try {
      await signIn({ email: email.trim(), password, rememberMe });
      setStatus("success");
      navigate({ to: "/", replace: true });
    } catch (caught: unknown) {
      const detail =
        (caught as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "We couldn't sign you in. Please check your credentials and try again.";
      setError(detail);
      setStatus("idle");
    }
  }

  return (
    <AuthLayout
      title="Sign in"
      subtitle="Enterprise Contract Intelligence Platform"
      footer={
        <span>
          Trouble signing in?{" "}
          <Link to="/forgot-password" className="text-jade hover:underline">
            Reset your password
          </Link>
        </span>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        {expired ? <FormMessage tone="error">Your session has expired.</FormMessage> : null}
        {error ? <FormMessage tone="error">{error}</FormMessage> : null}
        {status === "success" ? (
          <FormMessage tone="success">Signed in. Opening your workspace…</FormMessage>
        ) : null}

        <Field
          id="email"
          label="Work email"
          type="email"
          autoComplete="email"
          required
          aria-required="true"
          aria-invalid={Boolean(error)}
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="name@organisation.gov"
        />

        <div className="relative">
          <Field
            id="password"
            label="Password"
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            required
            aria-required="true"
            aria-invalid={Boolean(error)}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="pr-10"
          />
          <button
            type="button"
            onClick={() => setShowPassword((current) => !current)}
            aria-label={showPassword ? "Hide password" : "Show password"}
            className="absolute bottom-2.5 right-3 text-muted-foreground transition-colors hover:text-foreground"
          >
            {showPassword ? <EyeOff className="size-4" aria-hidden="true" /> : <Eye className="size-4" aria-hidden="true" />}
          </button>
        </div>

        <div className="flex items-center justify-between text-xs">
          <label className="flex cursor-pointer items-center gap-2 text-muted-foreground">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(event) => setRememberMe(event.target.checked)}
              className="size-3.5 rounded-sm accent-jade"
            />
            Remember me
          </label>
          <Link to="/forgot-password" className="text-muted-foreground hover:text-foreground">
            Forgot password?
          </Link>
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={status === "loading" || !email.trim() || !password}
          aria-busy={status === "loading"}
        >
          {status === "loading" ? <Loader2 className="animate-spin" aria-hidden="true" /> : null}
          {status === "loading" ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </AuthLayout>
  );
}
