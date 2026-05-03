"""Phase 11 — minimal latency / throughput / memory bench.

Runs against a live FastAPI service. Honours bearer auth via env
``MISINFO_API_KEY``. No external dependencies beyond the stdlib + httpx.

Usage::

    python scripts/perf_bench.py latency    --n 200
    python scripts/perf_bench.py throughput --n 100
    python scripts/perf_bench.py memory     --n 50

Writes a markdown table to ``reports/phase-11/perf-{mode}.md``.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import statistics
import sys
import time
import urllib.request
from pathlib import Path

DEFAULT_URL = os.environ.get("MISINFO_URL", "http://localhost:8000")
API_KEY = os.environ.get("MISINFO_API_KEY", "")
CLAIM = "The Eiffel Tower is in Paris."


def _post(url: str, body: bytes) -> tuple[int, float]:
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            **({"authorization": f"Bearer {API_KEY}"} if API_KEY else {}),
        },
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=120) as r:
        r.read()
        status = r.status
    return status, (time.perf_counter() - t0) * 1000.0


def _percentile(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def latency(n: int, url: str) -> str:
    body = json.dumps({"claim": CLAIM}).encode()
    samples: list[float] = []
    errors = 0
    for _ in range(n):
        try:
            status, ms = _post(f"{url}/v1/verify", body)
            (samples if status == 200 else []).append(ms)
            if status != 200:
                errors += 1
        except Exception:
            errors += 1
    p50 = _percentile(samples, 0.5)
    p95 = _percentile(samples, 0.95)
    return (
        "# Phase 11 — Latency\n\n"
        f"- requests: {n}\n- ok: {len(samples)}\n- errors: {errors}\n"
        f"- p50: {p50:.0f} ms\n- p95: {p95:.0f} ms\n"
        f"- mean: {statistics.fmean(samples):.0f} ms\n\n"
        "Budget: p50 ≤ 30000 ms, p95 ≤ 60000 ms (NFR-Lat-1).\n"
    )


def throughput(n: int, url: str) -> str:
    body = json.dumps({"claims": [CLAIM] * n}).encode()
    t0 = time.perf_counter()
    status, _ = _post(f"{url}/v1/batch", body)
    dur = time.perf_counter() - t0
    rate = n / dur if dur > 0 else 0.0
    return (
        "# Phase 11 — Throughput\n\n"
        f"- batch size: {n}\n- status: {status}\n- duration: {dur:.1f} s\n"
        f"- rate: {rate * 60:.1f} claims/min\n\n"
        "Budget: ≥ 10 claims/min (NFR-Tput).\n"
    )


def memory(n: int, url: str) -> str:
    body = json.dumps({"claim": CLAIM}).encode()
    rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    for _ in range(n):
        _post(f"{url}/v1/verify", body)
    rss_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return (
        "# Phase 11 — Memory (client-side RSS)\n\n"
        f"- requests: {n}\n- client rss before: {rss_before} KB\n"
        f"- client rss after: {rss_after} KB\n\n"
        "Note: this measures the bench client. Server-side memory is "
        "captured separately via container metrics in Grafana.\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("latency", "throughput", "memory"))
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--out", default="reports/phase-11")
    args = ap.parse_args()
    fn = {"latency": latency, "throughput": throughput, "memory": memory}[args.mode]
    md = fn(args.n, args.url)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"perf-{args.mode}.md").write_text(md)
    sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
