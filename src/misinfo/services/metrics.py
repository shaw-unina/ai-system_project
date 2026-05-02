"""Tiny in-process metrics store.

Exposes Prometheus text exposition format from a small set of counters and a
single latency histogram. Intentionally avoids the `prometheus-client` dep —
Phase 9 can swap this for the real client when monitoring goes in.
"""
from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field

LATENCY_BUCKETS = (0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)


@dataclass
class _MetricsStore:
    requests_total: dict[tuple[str, str], int] = field(default_factory=lambda: defaultdict(int))
    verdicts_total: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    bucket_counts: dict[float, int] = field(default_factory=lambda: defaultdict(int))
    latency_sum: float = 0.0
    latency_count: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def observe_request(self, endpoint: str, status: int, latency_s: float) -> None:
        with self._lock:
            self.requests_total[(endpoint, str(status))] += 1
            self.latency_sum += latency_s
            self.latency_count += 1
            for b in LATENCY_BUCKETS:
                if latency_s <= b:
                    self.bucket_counts[b] += 1
            self.bucket_counts[float("inf")] += 1

    def observe_verdict(self, verdict: str) -> None:
        with self._lock:
            self.verdicts_total[verdict] += 1

    def reset(self) -> None:
        with self._lock:
            self.requests_total.clear()
            self.verdicts_total.clear()
            self.bucket_counts.clear()
            self.latency_sum = 0.0
            self.latency_count = 0

    def render_prometheus(self) -> str:
        lines: list[str] = []
        lines.append("# HELP misinfo_requests_total Count of HTTP requests by endpoint and status.")
        lines.append("# TYPE misinfo_requests_total counter")
        for (endpoint, status), n in sorted(self.requests_total.items()):
            lines.append(f'misinfo_requests_total{{endpoint="{endpoint}",status="{status}"}} {n}')

        lines.append("# HELP misinfo_verdicts_total Count of verdicts emitted by label.")
        lines.append("# TYPE misinfo_verdicts_total counter")
        for verdict, n in sorted(self.verdicts_total.items()):
            lines.append(f'misinfo_verdicts_total{{verdict="{verdict}"}} {n}')

        lines.append("# HELP misinfo_latency_seconds Request end-to-end latency.")
        lines.append("# TYPE misinfo_latency_seconds histogram")
        for b in LATENCY_BUCKETS:
            lines.append(f'misinfo_latency_seconds_bucket{{le="{b}"}} {self.bucket_counts.get(b, 0)}')
        lines.append(
            f'misinfo_latency_seconds_bucket{{le="+Inf"}} '
            f'{self.bucket_counts.get(float("inf"), 0)}'
        )
        lines.append(f"misinfo_latency_seconds_sum {self.latency_sum:.6f}")
        lines.append(f"misinfo_latency_seconds_count {self.latency_count}")
        return "\n".join(lines) + "\n"


METRICS = _MetricsStore()
