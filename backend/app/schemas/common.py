from math import ceil
from typing import Any, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class ErrorItem(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    detail: str
    code: str
    errors: list[ErrorItem] | None = None  # hanya pada VALIDATION_ERROR


class MessageResponse(BaseModel):
    message: str


class PageParams:
    """Dependency paginasi: `params: Annotated[PageParams, Depends()]`."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Nomor halaman"),
        limit: int = Query(20, ge=1, le=100, description="Item per halaman"),
    ) -> None:
        self.page, self.limit = page, limit

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int

    @classmethod
    def build(cls, items: list[Any], total: int, params: PageParams) -> "Page[Any]":
        return cls(items=items, total=total, page=params.page, limit=params.limit,
                   pages=ceil(total / params.limit) if total else 0)


_DESC = {
    401: "UNAUTHORIZED - token tidak ada/kedaluwarsa/akun nonaktif",
    403: "FORBIDDEN - role tidak berhak atau bukan pemilik",
    404: "NOT_FOUND - data tidak ditemukan",
    409: "INVALID_STATUS_TRANSITION / DUPLICATE",
    422: "VALIDATION_ERROR - payload tidak valid",
    429: "TOO_MANY_REQUESTS",
}


def error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """Dokumentasi error di Swagger: `responses=error_responses(401, 403, 404)`."""
    return {c: {"model": ErrorResponse, "description": _DESC[c]} for c in codes}
