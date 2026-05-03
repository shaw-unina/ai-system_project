import LowConfidenceTable from "@/components/LowConfidenceTable";
import MetricsTiles from "@/components/MetricsTiles";
import ReportList from "@/components/ReportList";
import Tile from "@/components/operator/Tile";

export default function OperatorPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-brand-700">
          operator
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">
          Service health & cases
        </h1>
      </header>

      <MetricsTiles />

      <div className="grid gap-3 lg:grid-cols-3">
        <Tile title="Evaluation reports" className="lg:col-span-1">
          <ReportList />
        </Tile>
        <Tile
          title="Recent low-confidence verdicts"
          hint="kept in this browser only"
          className="lg:col-span-2"
          testId="lowconf-section"
        >
          <LowConfidenceTable />
        </Tile>
      </div>
    </div>
  );
}
