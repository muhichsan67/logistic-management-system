from typing import Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.schemas.common import PageParams

ModelT = TypeVar("ModelT", bound=Base)


async def paginate(
    db: AsyncSession, stmt: Select, params: PageParams, *,
    scalars: bool = True, count_stmt: Select | None = None,
) -> tuple[list, int]:
    """Helper reusable: kembalikan (rows, total).

    scalars=False -> baris tuple (untuk select multi-kolom). count_stmt opsional agar COUNT
    tidak membungkus statement berat (mis. yang punya join/kolom turunan)."""
    count_q = count_stmt if count_stmt is not None else select(func.count()).select_from(
        stmt.order_by(None).subquery()
    )
    total = await db.scalar(count_q) or 0
    paged = stmt.limit(params.limit).offset(params.offset)
    if scalars:
        return list((await db.scalars(paged)).all()), total
    return list((await db.execute(paged)).all()), total


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, id_: int) -> ModelT | None:
        return await self.db.get(self.model, id_)

    def add(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        return obj
