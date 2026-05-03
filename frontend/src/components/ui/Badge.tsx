import { HTMLAttributes, ReactNode } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset transition-colors",
  {
    variants: {
      tone: {
        neutral: "bg-muted text-muted-foreground ring-border",
        brand: "bg-brand-50 text-brand-800 ring-brand-100",
        info: "bg-accent-700/10 text-accent-700 ring-accent-700/20",
        supported:
          "bg-verdict-supported-bg text-verdict-supported ring-verdict-supported-ring",
        refuted:
          "bg-verdict-refuted-bg text-verdict-refuted ring-verdict-refuted-ring",
        unknown:
          "bg-verdict-unknown-bg text-verdict-unknown ring-verdict-unknown-ring",
        abstain:
          "bg-verdict-abstain-bg text-verdict-abstain ring-verdict-abstain-ring",
      },
    },
    defaultVariants: { tone: "neutral" },
  }
);

type BadgeProps = {
  children: ReactNode;
  className?: string;
} & VariantProps<typeof badgeVariants> &
  HTMLAttributes<HTMLSpanElement>;

export function Badge({ children, tone, className, ...rest }: BadgeProps) {
  return (
    <span {...rest} className={cn(badgeVariants({ tone }), className)}>
      {children}
    </span>
  );
}

export default Badge;
