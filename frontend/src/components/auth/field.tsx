import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export const Field = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement> & { label: string }
>(({ label, id, className, ...props }, ref) => (
  <div className="space-y-1.5">
    <label htmlFor={id} className="block text-xs font-medium text-muted-foreground">
      {label}
    </label>
    <input
      ref={ref}
      id={id}
      className={cn(
        "h-10 w-full rounded-md bg-secondary px-3 text-sm text-foreground outline-none ring-1 ring-transparent transition-[box-shadow,background-color] duration-150 placeholder:text-muted-foreground/60 focus-visible:bg-card focus-visible:ring-ring",
        className,
      )}
      {...props}
    />
  </div>
));
Field.displayName = "Field";

export function FormMessage({ tone, children }: { tone: "error" | "success"; children: string }) {
  return (
    <p
      role={tone === "error" ? "alert" : "status"}
      aria-live="polite"
      className={cn(
        "rise rounded-md px-3 py-2.5 text-xs",
        tone === "error" ? "bg-destructive/10 text-destructive" : "bg-jade/10 text-jade",
      )}
    >
      {children}
    </p>
  );
}
