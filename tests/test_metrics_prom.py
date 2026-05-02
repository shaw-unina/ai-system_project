"""Prometheus-client swap preserves the Phase 8 metric-name contract."""
from misinfo.services.metrics import METRICS


def test_metric_names_unchanged():
    METRICS.reset()
    METRICS.observe_request("/v1/verify", 200, 0.42)
    METRICS.observe_verdict("Supported", 0.8)
    text = METRICS.render_prometheus()
    assert "misinfo_requests_total" in text
    assert "misinfo_verdicts_total" in text
    assert "misinfo_latency_seconds_bucket" in text
    assert "misinfo_confidence" in text


def test_request_counter_increments():
    METRICS.reset()
    for _ in range(3):
        METRICS.observe_request("/v1/verify", 200, 0.1)
    text = METRICS.render_prometheus()
    line = next(
        l for l in text.splitlines()
        if l.startswith("misinfo_requests_total") and 'endpoint="/v1/verify"' in l
    )
    n = float(line.rsplit(" ", 1)[-1])
    assert n == 3.0


def test_verdict_observation_records_confidence():
    METRICS.reset()
    METRICS.observe_verdict("Refuted", 0.95)
    text = METRICS.render_prometheus()
    # Confidence histogram has a bucket count
    assert "misinfo_confidence_count" in text
    assert "misinfo_confidence_sum" in text
