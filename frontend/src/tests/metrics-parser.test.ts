import { parsePromText, summarise } from "@/lib/metrics";

const SAMPLE = `# HELP misinfo_requests_total ...
# TYPE misinfo_requests_total counter
misinfo_requests_total{endpoint="/v1/verify",status="200"} 7.0
misinfo_requests_total{endpoint="/healthz",status="200"} 3.0
# HELP misinfo_verdicts_total ...
# TYPE misinfo_verdicts_total counter
misinfo_verdicts_total{verdict="Supported"} 4.0
misinfo_verdicts_total{verdict="Abstain"} 1.0
# HELP misinfo_latency_seconds ...
# TYPE misinfo_latency_seconds histogram
misinfo_latency_seconds_bucket{le="0.1"} 2.0
misinfo_latency_seconds_bucket{le="0.5"} 8.0
misinfo_latency_seconds_bucket{le="1.0"} 9.0
misinfo_latency_seconds_bucket{le="+Inf"} 10.0
misinfo_latency_seconds_sum 1.234
misinfo_latency_seconds_count 10
`;

describe("parsePromText", () => {
  it("parses counters and histograms", () => {
    const samples = parsePromText(SAMPLE);
    expect(samples.length).toBeGreaterThan(5);
    const sample = samples.find(
      (s) => s.name === "misinfo_verdicts_total" && s.labels.verdict === "Supported",
    );
    expect(sample?.value).toBe(4);
  });
});

describe("summarise", () => {
  it("aggregates per endpoint and computes histogram quantiles", () => {
    const summary = summarise(parsePromText(SAMPLE));
    expect(summary.requestsTotal["/v1/verify"]).toBe(7);
    expect(summary.verdictsTotal.Abstain).toBe(1);
    expect(summary.latencyP50).not.toBeNull();
    expect(summary.latencyP95).not.toBeNull();
    expect(summary.latencyP50!).toBeLessThanOrEqual(summary.latencyP95!);
  });

  it("returns null quantiles when no observations", () => {
    const summary = summarise(parsePromText("# nothing\n"));
    expect(summary.latencyP50).toBeNull();
    expect(summary.latencyCount).toBe(0);
  });
});
