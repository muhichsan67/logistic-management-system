from collections.abc import Mapping
from typing import NoReturn

from fastapi import HTTPException, status


STATUS_ERROR_CODES = {
    status.HTTP_400_BAD_REQUEST: "VALIDATION_ERROR",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_409_CONFLICT: "INVALID_STATUS_TRANSITION",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_ERROR",
}


def error_payload(
    detail: str,
    status_code: int,
    code: str | None = None,
) -> dict[str, str]:
    return {
        "detail": detail,
        "code": code or STATUS_ERROR_CODES.get(status_code, "INTERNAL_ERROR"),
    }


def raise_api_error(
    status_code: int,
    detail: str,
    code: str | None = None,
) -> NoReturn:
    raise HTTPException(
        status_code=status_code,
        detail=error_payload(detail, status_code, code),
        headers=(
            {"WWW-Authenticate": "Bearer"}
            if status_code == status.HTTP_401_UNAUTHORIZED
            else None
        ),
    )


def normalize_http_error(
    detail: object,
    status_code: int,
) -> dict[str, str]:
    if isinstance(detail, Mapping):
        message = detail.get("detail")
        code = detail.get("code")
        if isinstance(message, str) and isinstance(code, str):
            return {"detail": message, "code": code}

    return error_payload(str(detail), status_code)
