"""Prometheus-client backed metrics. Phase 9 swap of the Phase 8 in-process store.

Public API kept identical to Phase 8 so the API tests + endpoint contract are
unchanged. Same metric names; histograms gain a `confidence` series so the
Grafana dashboard can render verdict-confidence over time.
"""
from __future__ import annotations

import threading

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

LATENCY_BUCKETS = (0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
CONFIDENCE_BUCKETS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)

# Sentinel registry constructed once; metrics live on it. Test-only `reset()`
# rebuilds the metrics on a fresh registry to keep test isolation clean.
_lock = threading.Lock()


class _Metrics:
    def __init__(self) -> None:
        self._build()

    def _build(self) -> None:
        # Use a private registry so we can wipe it on reset() without colliding
        # with anything else in the default REGISTRY.
        self._registry = CollectorRegistry()
        self.requests = Counter(
            "misinfo_requests_total",
            "Count of HTTP requests by endpoint and status.",
            ["endpoint", "status"],
            registry=self._registry,
        )
        self.verdicts = Counter(
            "misinfo_verdicts_total",
            "Count of verdicts emitted by label.",
            ["verdict"],
            registry=self._registry,
        )
        self.latency = Histogram(
            "misinfo_latency_seconds",
            "Request end-to-end latency in seconds.",
            buckets=LATENCY_BUCKETS,
            registry=self._registry,
        )
        self.confidence = Histogram(
            "misinfo_confidence",
            "Distribution of verdict confidences.",
            buckets=CONFIDENCE_BUCKETS,
            registry=self._registry,
        )

    def observe_request(self, endpoint: str, status: int, latency_s: float) -> None:
        with _lock:
            self.requests.labels(endpoint=endpoint, status=str(status)).inc()
            self.latency.observe(latency_s)

    def observe_verdict(self, verdict: str, confidence: float | None = None) -> None:
        with _lock:
            self.verdicts.labels(verdict=verdict).inc()
            if confidence is not None:
                self.confidence.observe(float(confidence))

    def reset(self) -> None:
        with _lock:
            self._build()

    def render_prometheus(self) -> str:
        return generate_latest(self._registry).decode("utf-8")


METRICS = _Metrics()
