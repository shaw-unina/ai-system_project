"""FastAPI app factory + module-level `app` for uvicorn.

Routes:
    POST /v1/verify    — single-claim verification
    POST /v1/batch     — multi-claim verification (≤ 100)
    GET  /healthz      — liveness
    GET  /readyz       — readiness (backend + head + tau)
    GET  /version      — package + model version
    GET  /metrics      — Prometheus text exposition
"""
from __future__ import annotations

import time
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from misinfo import __version__
from misinfo.config import get_settings
from misinfo.repro import git_sha
from misinfo.services.deps import get_factchecker
from misinfo.services.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from misinfo.services.metrics import METRICS
from misinfo.services.middleware import RequestIdMiddleware, StructuredLogMiddleware
from misinfo.services.schemas import (
    LOW_CONFIDENCE_THRESHOLD,
    BatchRequest,
    BatchResponse,
    HealthResponse,
    ReadyResponse,
    VerifyRequest,
    VerifyResponse,
    VersionResponse,
)


def _to_response(verdict, request_id: str, latency_ms: float) -> VerifyResponse:
    METRICS.observe_verdict(verdict.verdict)
    return VerifyResponse(
        verdict=verdict.verdict,
        confidence=verdict.confidence,
        evidence=verdict.evidence,
        rationale=verdict.rationale,
        metadata=verdict.metadata,
        low_confidence=(
            verdict.verdict == "Abstain" or verdict.confidence < LOW_CONFIDENCE_THRESHOLD
        ),
        request_id=request_id,
        latency_ms=latency_ms,
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="misinfo",
        version=__version__,
        description="LLM-based misinformation detector — see /docs.",
    )
    app.add_middleware(StructuredLogMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.get("/healthz", response_model=HealthResponse)
    def healthz() -> HealthResponse:
        return HealthResponse()

    @app.get("/readyz", response_model=ReadyResponse)
    def readyz(fc: Any = Depends(get_factchecker)) -> ReadyResponse:
        s = get_settings()
        head = type(getattr(fc, "_abstention", None)).__name__ if fc else None
        tau = getattr(fc, "_tau", None)
        return ReadyResponse(ready=True, backend=s.misinfo_backend, head=head, tau=tau)

    @app.get("/version", response_model=VersionResponse)
    def version(fc: Any = Depends(get_factchecker)) -> VersionResponse:
        return VersionResponse(
            name="misinfo",
            version=__version__,
            git_sha=git_sha(),
            model_id=getattr(fc, "_model_id", "unknown") or "unknown",
            model_version=getattr(fc, "_model_version", None),
        )

    @app.get("/metrics")
    def metrics() -> PlainTextResponse:
        return PlainTextResponse(METRICS.render_prometheus(), media_type="text/plain")

    @app.post("/v1/verify", response_model=VerifyResponse)
    def verify(
        body: VerifyRequest,
        request: Request,
        fc: Any = Depends(get_factchecker),
    ) -> VerifyResponse:
        rid = request.state.request_id
        t0 = time.perf_counter()
        verdict = fc.verify(body.claim)
        latency_ms = 1000.0 * (time.perf_counter() - t0)
        return _to_response(verdict, rid, latency_ms)

    @app.post("/v1/batch", response_model=BatchResponse)
    def batch(
        body: BatchRequest,
        request: Request,
        fc: Any = Depends(get_factchecker),
    ) -> BatchResponse:
        rid = request.state.request_id
        results = []
        for claim in body.claims:
            t0 = time.perf_counter()
            verdict = fc.verify(claim)
            latency_ms = 1000.0 * (time.perf_counter() - t0)
            results.append(_to_response(verdict, rid, latency_ms))
        return BatchResponse(results=results)

    return app


app = create_app()
