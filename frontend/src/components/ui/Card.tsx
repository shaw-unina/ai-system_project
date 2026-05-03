import { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Card({
  children,
  className,
  ...rest
}: { children: ReactNode; className?: string } & HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-border bg-card text-card-foreground shadow-soft",
        className
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  title,
  hint,
  right,
  className,
}: {
  title: ReactNode;
  hint?: ReactNode;
  right?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex items-start justify-between gap-3 border-b border-border px-5 py-3",
        className
      )}
    >
      <div>
        <div className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
          {title}
        </div>
        {hint && <div className="mt-0.5 text-xs text-muted-foreground">{hint}</div>}
      </div>
      {right && <div className="text-xs text-muted-foreground">{right}</div>}
    </div>
  );
}

export default Card;
