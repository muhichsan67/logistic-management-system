from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SystemSetting

# Fallback bila baris di system_settings hilang/rusak. Nilai sebenarnya dikelola Admin di DB.
_FALLBACK = {"pending_alert_timeout_minutes": 30, "auto_complete_days": 3}


async def get_int_setting(db: AsyncSession, key: str) -> int:
    row = await db.get(SystemSetting, key)
    try:
        value = int(row.value) if row else _FALLBACK[key]
    except ValueError:
        return _FALLBACK[key]
    return value if value > 0 else _FALLBACK[key]


async def get_all_settings(db: AsyncSession) -> dict[str, str]:
    """Selalu mengembalikan semua key yang dikenal (fallback bila baris hilang)."""
    result = {k: str(v) for k, v in _FALLBACK.items()}
    for row in (await db.scalars(select(SystemSetting))).all():
        if row.key in result:
            result[row.key] = row.value
    return result


async def update_settings(db: AsyncSession, values: dict[str, str]) -> None:
    for key, value in values.items():
        if key not in _FALLBACK:  # whitelist: key lain tidak boleh disentuh
            continue
        row = await db.get(SystemSetting, key)
        if row is None:
            db.add(SystemSetting(key=key, value=value))
        else:
            row.value = value
    await db.commit()
