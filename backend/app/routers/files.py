"""Menyajikan foto bukti pengiriman: dari disk (foto lama) atau redirect ke URL presigned S3.

Router ini didaftarkan LANGSUNG di app (bukan di bawah /api/v1) agar path-nya sama dengan
`proof_image_url` yang disimpan di DB (`/static/proofs/<nama>`), dan harus didaftarkan
SEBELUM mount StaticFiles.
"""
import asyncio
import re
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.services.upload_service import presign_proof_url

router = APIRouter(include_in_schema=False)
_NAME = re.compile(r"^[0-9a-f]{32}\.(jpg|png)$")


@router.get(f"{get_settings().UPLOAD_URL_PREFIX}/proofs/{{name}}")
async def proof_file(name: str):
    if not _NAME.fullmatch(name):  # tolak path aneh
        raise NotFoundError()
    s = get_settings()
    local = Path(s.UPLOAD_DIR) / "proofs" / name
    if local.is_file():  # foto lama / mode local
        return FileResponse(local)
    if s.STORAGE_BACKEND != "s3":
        raise NotFoundError()
    url = await asyncio.to_thread(presign_proof_url, name)
    return RedirectResponse(url, status_code=302,
                            headers={"Cache-Control": "private, max-age=120"})
