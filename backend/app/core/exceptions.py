"""Exception domain + handler global. Format error seragam: {"detail", "code"}."""
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.errors")


class AppException(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"
    default_detail = "Terjadi kesalahan pada server."

    def __init__(
        self,
        detail: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        self.detail = detail or self.default_detail
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.errors = errors
        super().__init__(self.detail)


class ValidationFailed(AppException):
    status_code = 422
    code = "VALIDATION_ERROR"
    default_detail = "Data yang dikirim tidak valid."


class UnauthorizedError(AppException):
    status_code = 401
    code = "UNAUTHORIZED"
    default_detail = "Token tidak ada, tidak valid, atau kedaluwarsa."


class ForbiddenError(AppException):
    status_code = 403
    code = "FORBIDDEN"
    default_detail = "Anda tidak berhak mengakses sumber daya ini."


class NotFoundError(AppException):
    status_code = 404
    code = "NOT_FOUND"
    default_detail = "Data tidak ditemukan."


class DuplicateError(AppException):
    status_code = 409
    code = "DUPLICATE"
    default_detail = "Data sudah terdaftar."


class InvalidStatusTransition(AppException):
    status_code = 409
    code = "INVALID_STATUS_TRANSITION"
    default_detail = "Transisi status tidak diizinkan."


class TooManyRequests(AppException):
    status_code = 429
    code = "TOO_MANY_REQUESTS"
    default_detail = "Terlalu banyak percobaan. Coba lagi nanti."


_STATUS_TO_CODE = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "DUPLICATE",
    429: "TOO_MANY_REQUESTS",
}


def _body(detail: str, code: str, errors: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"detail": detail, "code": code}
    if errors:
        body["errors"] = errors
    return body


def _headers(status_code: int) -> dict[str, str] | None:
    return {"WWW-Authenticate": "Bearer"} if status_code == 401 else None


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exc_handler(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            _body(exc.detail, exc.code, exc.errors), exc.status_code, _headers(exc.status_code)
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Sengaja tidak menyertakan `input` agar password tidak bocor ke respons.
        errors = [
            {"field": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]), "message": e["msg"].removeprefix("Value error, ")}
            for e in exc.errors()
        ]
        return JSONResponse(
            _body("Data yang dikirim tidak valid.", "VALIDATION_ERROR", errors), 422
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _STATUS_TO_CODE.get(exc.status_code, "INTERNAL_ERROR" if exc.status_code >= 500 else "ERROR")
        return JSONResponse(
            _body(str(exc.detail), code), exc.status_code, _headers(exc.status_code)
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error", exc_info=exc)  # stack trace hanya di log
        return JSONResponse(_body("Terjadi kesalahan pada server.", "INTERNAL_ERROR"), 500)
