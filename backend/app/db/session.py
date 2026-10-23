from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

_s = get_settings()

engine = create_async_engine(
    _s.DATABASE_URL,
    pool_size=_s.DB_POOL_SIZE,
    max_overflow=_s.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=_s.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
