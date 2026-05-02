"""HTTP error envelope + handlers."""
from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from misinfo.services.schemas import ErrorEnvelope


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    body = ErrorEnvelope(
        error=exc.__class__.__name__,
        detail=str(exc.detail),
        request_id=_request_id(request),
    ).model_dump()
    return JSONResponse(status_code=exc.status_code, content=body)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    body = ErrorEnvelope(
        error="ValidationError",
        detail=str(exc.errors()),
        request_id=_request_id(request),
    ).model_dump()
    return JSONResponse(status_code=422, content=body)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    body = ErrorEnvelope(
        error=exc.__class__.__name__,
        detail=str(exc),
        request_id=_request_id(request),
    ).model_dump()
    return JSONResponse(status_code=500, content=body)
