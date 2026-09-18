import { createFileRoute, Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Eye, EyeOff, Loader2 } from "lucide-react";
import { AuthLayout } from "@/components/auth/auth-layout";
import { Field, FormMessage } from "@/components/auth/field";
import { Button } from "@/components/ui/button";
import { submitNewPassword } from "@/lib/auth/auth-api";

export const Route = createFileRoute("/reset-password")({
  head: () => ({
    meta: [
      { title: "Set a new password | ContractIQ" },
      { name: "description", content: "Choose a new password for your ContractIQ account." },
      { property: "og:title", content: "Set a new password | ContractIQ" },
      {
        property: "og:description",
        content: "Choose a new password for your ContractIQ account.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: ResetPasswordPage,
});

function scorePassword(value: string) {
  let score = 0;
  if (value.length >= 8) score += 1;
  if (value.length >= 12) score += 1;
  if (/[A-Z]/.test(value) && /[a-z]/.test(value)) score += 1;
  if (/\d/.test(value)) score += 1;
  if (/[^A-Za-z0-9]/.test(value)) score += 1;
  return Math.min(score, 4);
}

const strengthLabels = ["Too short", "Weak", "Fair", "Strong", "Excellent"];

function ResetPasswordPage() {
  const navigate = useNavigate();
  const token =
    useRouterState({ select: (state) => state.location.search as { token?: string } }).token ?? "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState<"idle" | "loading" | "done">("idle");
  const [error, setError] = useState<string | null>(null);

  const strength = useMemo(() => scorePassword(password), [password]);

  useEffect(() => {
    if (status !== "done") return;
    const timer = setTimeout(() => navigate({ to: "/login", replace: true }), 2500);
    return () => clearTimeout(timer);
  }, [status, navigate]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (!password) {
      setError("Please enter a new password.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (!confirmPassword) {
      setError("Please confirm your new password.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Both passwords must match.");
      return;
    }
    setStatus("loading");
    try {
      await submitNewPassword({ token, password });
      setStatus("done");
    } catch (caught: unknown) {
      setError(caught instanceof Error ? caught.message : "Something went wrong. Try again.");
      setStatus("idle");
    }
  }

  if (status === "done") {
    return (
      <AuthLayout title="Password updated" subtitle="You can now sign in with your new password.">
        <div className="rise space-y-6">
          <CheckCircle2 className="size-8 text-jade" aria-hidden="true" />
          <p className="text-sm text-muted-foreground">
            Redirecting you to the sign-in page in a moment.
          </p>
          <Button asChild className="w-full">
            <Link to="/login">Continue to sign in</Link>
          </Button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Set a new password"
      subtitle="Choose a password you haven't used before."
      footer={
        <Link to="/login" className="hover:text-foreground">
          Back to sign in
        </Link>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        {error ? <FormMessage tone="error">{error}</FormMessage> : null}

        <div className="relative">
          <Field
            id="new-password"
            label="New password"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
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

        <div>
          <div className="flex gap-1" aria-hidden="true">
            {[0, 1, 2, 3].map((index) => (
              <span
                key={index}
                className={
                  index < strength
                    ? "h-0.5 flex-1 rounded-full bg-jade transition-colors duration-200"
                    : "h-0.5 flex-1 rounded-full bg-border transition-colors duration-200"
                }
              />
            ))}
          </div>
          <p className="mt-2 text-xs text-muted-foreground">Strength: {strengthLabels[strength]}</p>
        </div>

        <Field
          id="confirm-password"
          label="Confirm password"
          type={showPassword ? "text" : "password"}
          autoComplete="new-password"
          required
          aria-required="true"
          aria-invalid={Boolean(error)}
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
        />

        <Button
          type="submit"
          className="w-full"
          disabled={status === "loading" || !password || !confirmPassword}
          aria-busy={status === "loading"}
        >
          {status === "loading" ? <Loader2 className="animate-spin" aria-hidden="true" /> : null}
          {status === "loading" ? "Updating…" : "Reset password"}
        </Button>
      </form>
    </AuthLayout>
  );
}
