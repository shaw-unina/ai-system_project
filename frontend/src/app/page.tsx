export default function Home() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">misinfo dashboard</h1>
      <p className="text-slate-700">
        Local-only operator surface for the LLM-based misinformation detector. Two
        views:
      </p>
      <ul className="list-disc list-inside text-slate-700 space-y-1">
        <li>
          <a className="text-blue-700 underline" href="/verify">
            /verify
          </a>{" "}
          — submit a claim, see a calibrated verdict with evidence, rationale, and
          confidence.
        </li>
        <li>
          <a className="text-blue-700 underline" href="/operator">
            /operator
          </a>{" "}
          — live <code>/metrics</code> tiles, Phase 7 reports, and recent
          low-confidence cases.
        </li>
      </ul>
      <p className="text-xs text-slate-500">
        Built against the Phase 8 FastAPI service (<code>VerifyResponse</code>) and
        the Phase 9 <code>/metrics</code> exposition.
      </p>
    </div>
  );
}
