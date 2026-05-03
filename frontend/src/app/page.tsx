export default function Home() {
  return (
    <div className="mx-auto max-w-3xl space-y-16 py-8">
      <section className="space-y-6">
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-brand-700">
          misinfo · v1
        </p>
        <h1 className="font-display text-5xl font-semibold leading-[1.05] tracking-tight text-ink sm:text-6xl">
          Closed-book verification
          <br />
          for short factual claims.
        </h1>
        <p className="max-w-2xl text-lg leading-relaxed text-ink-muted">
          Submit a claim. The system retrieves evidence, asks an LLM to score it,
          and returns a verdict with calibrated confidence and a rationale you
          can audit. Every output is AI-generated and traceable.
        </p>
        <div className="flex flex-wrap items-center gap-3">
          <a
            href="/verify"
            className="inline-flex cursor-pointer items-center gap-2 rounded-full bg-brand-700 px-5 py-2.5 text-sm font-medium text-white shadow-soft transition-colors hover:bg-brand-800"
          >
            Try it
            <span aria-hidden>→</span>
          </a>
          <a
            href="/operator"
            className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-border bg-card px-5 py-2.5 text-sm font-medium text-ink transition-colors hover:border-foreground/30"
          >
            For operators
          </a>
        </div>
      </section>

      <section className="grid gap-6 border-t border-border pt-12 sm:grid-cols-3">
        <Feature
          eyebrow="Grounded"
          title="Live web evidence"
          body="Each sub-question is searched independently, with an optional second opinion from established fact-checkers."
        />
        <Feature
          eyebrow="Calibrated"
          title="Honest confidence"
          body="Confidence is calibrated against a held-out evaluation set, and the system abstains when evidence is thin."
        />
        <Feature
          eyebrow="Auditable"
          title="Traceable output"
          body="Every verdict carries the supporting evidence and a stable identifier you can reference later."
        />
      </section>

    </div>
  );
}

function Feature({
  eyebrow,
  title,
  body,
}: {
  eyebrow: string;
  title: string;
  body: string;
}) {
  return (
    <div>
      <p className="font-mono text-[10px] uppercase tracking-wider text-brand-700">
        {eyebrow}
      </p>
      <h3 className="mt-1 font-display text-lg font-semibold text-ink">{title}</h3>
      <p className="mt-1 text-sm leading-relaxed text-ink-muted">{body}</p>
    </div>
  );
}
