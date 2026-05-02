"""Latency probe — POSTs N synthetic claims and reports p50 / p95."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LatencyReport:
    n: int
    mean_ms: float
    p50_ms: float
    p95_ms: float
    errors: int


def probe_latency(client, *, n: int = 20, path: str = "/v1/verify") -> LatencyReport:
    """`client` may be httpx.Client, httpx.AsyncClient (sync usage shown), or
    fastapi.testclient.TestClient — anything with a `.post(path, json=...)`."""
    import time

    latencies: list[float] = []
    errors = 0
    for i in range(n):
        t0 = time.perf_counter()
        try:
            r = client.post(path, json={"claim": f"probe claim {i}"})
            if r.status_code >= 400:
                errors += 1
                continue
        except Exception:
            errors += 1
            continue
        latencies.append(1000.0 * (time.perf_counter() - t0))

    if not latencies:
        return LatencyReport(n=n, mean_ms=0.0, p50_ms=0.0, p95_ms=0.0, errors=errors)

    arr = np.asarray(latencies)
    return LatencyReport(
        n=n,
        mean_ms=float(arr.mean()),
        p50_ms=float(np.quantile(arr, 0.5)),
        p95_ms=float(np.quantile(arr, 0.95)),
        errors=errors,
    )
