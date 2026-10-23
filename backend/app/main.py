import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware
from app.db.session import engine
from app.jobs.auto_complete import create_scheduler
from app.routers import api_router, files

logger = logging.getLogger("app")

TAGS = [
    {"name": "Auth", "description": "Registrasi, login, refresh & logout"},
    {"name": "Shipments", "description": "Aksi Customer + pelacakan publik"},
    {"name": "Courier", "description": "Tugas & update status Kurir"},
    {"name": "Uploads", "description": "Upload bukti pengiriman"},
    {"name": "Admin", "description": "Manajemen Admin"},
    {"name": "Health", "description": "Health check"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    s = get_settings()
    scheduler = create_scheduler() if s.SCHEDULER_ENABLED else None
    if scheduler:
        scheduler.start()
    logger.info("Aplikasi dimulai (%s)", s.ENVIRONMENT)
    yield
    if scheduler:
        scheduler.shutdown(wait=False)
    await engine.dispose()


def create_app() -> FastAPI:
    s = get_settings()
    setup_logging(s.DEBUG)

    app = FastAPI(
        title=s.APP_NAME, version=s.APP_VERSION, openapi_tags=TAGS, lifespan=lifespan,
        description="API sistem pelacakan paket **ALUR Logistik**. Klik **Authorize** dan tempel "
                    "`access_token` dari `/auth/login`.",
        docs_url=None if s.is_production else "/docs",
        redoc_url=None if s.is_production else "/redoc",
        openapi_url=None if s.is_production else f"{s.API_V1_PREFIX}/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=s.CORS_ORIGINS, allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"], expose_headers=["X-Request-ID"],
    )
    app.add_middleware(RequestIDMiddleware)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=s.API_V1_PREFIX)

    app.include_router(files.router)  # harus SEBELUM mount StaticFiles di bawah
    Path(s.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    app.mount(s.UPLOAD_URL_PREFIX, StaticFiles(directory=s.UPLOAD_DIR), name="static")
    return app


app = create_app()
