from fastapi import APIRouter
from sqlalchemy import text

from app.core.deps import DBSession
from app.core.exceptions import AppException

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Cek aplikasi & database")
async def health(db: DBSession) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise AppException("Database tidak tersedia.", code="SERVICE_UNAVAILABLE",
                           status_code=503) from exc
    return {"status": "ok", "database": "up"}
