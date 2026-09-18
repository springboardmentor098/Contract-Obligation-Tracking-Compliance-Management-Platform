import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowLeft, Loader2 } from "lucide-react";
import { AuthLayout } from "@/components/auth/auth-layout";
import { Field, FormMessage } from "@/components/auth/field";
import { Button } from "@/components/ui/button";
import { requestPasswordResetLink } from "@/lib/auth/auth-api";

export const Route = createFileRoute("/forgot-password")({
  head: () => ({
    meta: [
      { title: "Reset your password | ContractIQ" },
      {
        name: "description",
        content: "Request a password reset link for your ContractIQ account.",
      },
      { property: "og:title", content: "Reset your password | ContractIQ" },
      {
        property: "og:description",
        content: "Request a password reset link for your ContractIQ account.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: ForgotPasswordPage,
});

function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "sent">("idle");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (!email.trim()) {
      setError("Please enter your work email address.");
      return;
    }
    setStatus("loading");
    try {
      await requestPasswordResetLink(email.trim());
      setStatus("sent");
    } catch (caught: unknown) {
      setError(caught instanceof Error ? caught.message : "Something went wrong. Try again.");
      setStatus("idle");
    }
  }

  return (
    <AuthLayout
      title="Forgot password"
      subtitle="We'll email you a secure link to set a new password."
      footer={
        <Link
          to="/login"
          className="inline-flex items-center gap-1.5 hover:text-foreground"
          aria-label="Back to sign in page"
        >
          <ArrowLeft className="size-3.5" aria-hidden="true" /> Back to sign in
        </Link>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        {error ? <FormMessage tone="error">{error}</FormMessage> : null}
        {status === "sent" ? (
          <FormMessage tone="success">
            If an account exists for this address, a reset link is on its way.
          </FormMessage>
        ) : null}

        <Field
          id="reset-email"
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

        <Button
          type="submit"
          className="w-full"
          disabled={status === "loading" || !email.trim()}
          aria-busy={status === "loading"}
        >
          {status === "loading" ? <Loader2 className="animate-spin" aria-hidden="true" /> : null}
          {status === "loading" ? "Sending…" : "Send reset link"}
        </Button>
      </form>
    </AuthLayout>
  );
}
