import asyncio

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError

from core.errors import error_payload, normalize_http_error, raise_api_error
from main import http_exception_handler, validation_exception_handler


def run(awaitable):
    return asyncio.run(awaitable)


def test_error_payload_uses_standard_code():
    assert error_payload(
        "Not found",
        status.HTTP_404_NOT_FOUND,
    ) == {
        "detail": "Not found",
        "code": "NOT_FOUND",
    }


def test_normalize_http_error_prevents_nested_detail():
    assert normalize_http_error(
        {"detail": "Forbidden", "code": "FORBIDDEN"},
        status.HTTP_403_FORBIDDEN,
    ) == {
        "detail": "Forbidden",
        "code": "FORBIDDEN",
    }


def test_normalize_http_error_maps_string_detail():
    assert normalize_http_error(
        "Invalid token",
        status.HTTP_401_UNAUTHORIZED,
    ) == {
        "detail": "Invalid token",
        "code": "UNAUTHORIZED",
    }


def test_raise_api_error_creates_standard_exception():
    try:
        raise_api_error(
            status.HTTP_409_CONFLICT,
            "Invalid status transition",
        )
    except HTTPException as exc:
        assert exc.detail == {
            "detail": "Invalid status transition",
            "code": "INVALID_STATUS_TRANSITION",
        }
    else:
        raise AssertionError("raise_api_error did not raise")


def test_http_exception_handler_returns_standard_json():
    request = Request({"type": "http", "method": "GET", "path": "/"})
    response = run(
        http_exception_handler(
            request,
            HTTPException(
                status_code=404,
                detail={"detail": "Missing", "code": "NOT_FOUND"},
            ),
        )
    )

    assert response.status_code == 404
    assert response.body == b'{"detail":"Missing","code":"NOT_FOUND"}'


def test_validation_exception_handler_returns_validation_error():
    request = Request({"type": "http", "method": "POST", "path": "/"})
    response = run(
        validation_exception_handler(
            request,
            RequestValidationError(
                [
                    {
                        "type": "missing",
                        "loc": ("body", "name"),
                        "msg": "Field required",
                        "input": {},
                    }
                ]
            ),
        )
    )

    assert response.status_code == 422
    assert response.body == (
        b'{"detail":"Request validation failed","code":"VALIDATION_ERROR"}'
    )
