"""Request-ID, structured logging, and metrics middleware."""
from __future__ import annotations

import hashlib
import os
import time
import uuid

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from misinfo.services.metrics import METRICS


def _log_claims_enabled() -> bool:
    return os.environ.get("MISINFO_LOG_CLAIMS", "false").lower() in ("1", "true", "yes")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = rid
        response: Response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        return response


class StructuredLogMiddleware(BaseHTTPMiddleware):
    """JSON-ish access log via loguru. Redacts claim text by default."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        body_preview = ""
        if request.method == "POST" and request.url.path.startswith("/v1/"):
            body = await request.body()
            # Re-attach for downstream consumers
            request._body = body  # type: ignore[attr-defined]
            if _log_claims_enabled():
                body_preview = body.decode("utf-8", errors="replace")[:500]
            else:
                body_preview = (
                    f"<redacted len={len(body)} sha8={hashlib.sha256(body).hexdigest()[:8]}>"
                )

        response: Response = await call_next(request)
        latency_s = time.perf_counter() - start
        METRICS.observe_request(request.url.path, response.status_code, latency_s)

        logger.info(
            "http",
            request_id=getattr(request.state, "request_id", None),
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            latency_ms=round(latency_s * 1000, 2),
            body_preview=body_preview,
        )
        return response
