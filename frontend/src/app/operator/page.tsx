import LowConfidenceTable from "@/components/LowConfidenceTable";
import MetricsTiles from "@/components/MetricsTiles";
import ReportList from "@/components/ReportList";

export default function OperatorPage() {
  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-semibold mb-3">Operator dashboard</h1>
        <p className="text-sm text-slate-600">
          Live tiles poll <code>/metrics</code> every 10 s. Reports come from{" "}
          <code>reports/_smoke/</code>; switch to <code>reports/phase7/</code>{" "}
          once a real run lands.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-2">Live tiles</h2>
        <MetricsTiles />
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-2">Phase 7 reports</h2>
        <ReportList />
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-2">
          Recent low-confidence verdicts (this session)
        </h2>
        <LowConfidenceTable />
      </section>
    </div>
  );
}
