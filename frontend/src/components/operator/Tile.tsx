import { ReactNode } from "react";
import Card, { CardHeader } from "@/components/ui/Card";

export function Tile({
  title,
  hint,
  right,
  className = "",
  children,
  testId,
}: {
  title: string;
  hint?: ReactNode;
  right?: ReactNode;
  className?: string;
  children: ReactNode;
  testId?: string;
}) {
  return (
    <Card className={`overflow-hidden ${className}`} data-testid={testId}>
      <CardHeader title={title} hint={hint} right={right} />
      <div className="p-5">{children}</div>
    </Card>
  );
}

export function KpiTile({
  title,
  value,
  unit,
  hint,
  testId,
}: {
  title: string;
  value: string | number;
  unit?: string;
  hint?: string;
  testId?: string;
}) {
  return (
    <Tile title={title} hint={hint} testId={testId}>
      <div className="flex items-baseline gap-1">
        <div className="font-display text-3xl font-semibold leading-none tabular-nums text-ink">
          {value}
        </div>
        {unit && <div className="text-sm text-ink-muted">{unit}</div>}
      </div>
    </Tile>
  );
}

export default Tile;
