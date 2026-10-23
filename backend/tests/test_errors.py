import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.exceptions import (
    AppException,
    DuplicateError,
    ForbiddenError,
    InvalidStatusTransition,
    NotFoundError,
    TooManyRequests,
    UnauthorizedError,
    ValidationFailed,
    _body,
    register_exception_handlers,
)


def test_app_exception_defaults_to_internal_error():
    exc = AppException()
    assert exc.status_code == 500
    assert exc.code == "INTERNAL_ERROR"
    assert exc.detail == "Terjadi kesalahan pada server."


@pytest.mark.parametrize(
    ("cls", "status_code", "code"),
    [
        (ValidationFailed, 422, "VALIDATION_ERROR"),
        (UnauthorizedError, 401, "UNAUTHORIZED"),
        (ForbiddenError, 403, "FORBIDDEN"),
        (NotFoundError, 404, "NOT_FOUND"),
        (DuplicateError, 409, "DUPLICATE"),
        (InvalidStatusTransition, 409, "INVALID_STATUS_TRANSITION"),
        (TooManyRequests, 429, "TOO_MANY_REQUESTS"),
    ],
)
def test_domain_exceptions_carry_standard_http_contract(cls, status_code, code):
    exc = cls("pesan")
    assert exc.status_code == status_code
    assert exc.code == code
    assert exc.detail == "pesan"


def test_body_builds_standard_payload():
    assert _body("Not found", "NOT_FOUND") == {"detail": "Not found", "code": "NOT_FOUND"}
    assert _body("Bad", "VALIDATION_ERROR", [{"field": "a", "message": "m"}]) == {
        "detail": "Bad",
        "code": "VALIDATION_ERROR",
        "errors": [{"field": "a", "message": "m"}],
    }


def _make_app():
    class Body(BaseModel):
        name: str

    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/not-found")
    async def not_found():
        raise NotFoundError("Data tidak ditemukan.")

    @app.get("/conflict")
    async def conflict():
        raise InvalidStatusTransition("Transisi status tidak diizinkan.")

    @app.get("/unauthorized")
    async def unauthorized():
        raise UnauthorizedError()

    @app.post("/validate")
    async def validate(body: Body):
        return body

    return app


async def test_not_found_handler_returns_standard_json():
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/not-found")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Data tidak ditemukan.", "code": "NOT_FOUND"}


async def test_conflict_handler_returns_standard_json():
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/conflict")
    assert resp.status_code == 409
    assert resp.json() == {"detail": "Transisi status tidak diizinkan.", "code": "INVALID_STATUS_TRANSITION"}


async def test_unauthorized_handler_adds_bearer_header():
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/unauthorized")
    assert resp.status_code == 401
    assert resp.headers["WWW-Authenticate"] == "Bearer"
    assert resp.json()["code"] == "UNAUTHORIZED"


async def test_validation_handler_returns_422_with_code():
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/validate", json={})
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["detail"] == "Data yang dikirim tidak valid."
