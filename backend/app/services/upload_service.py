import asyncio
import logging
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import AppException, ValidationFailed

logger = logging.getLogger("app.upload")
# Validasi berdasarkan ISI file (magic bytes), bukan ekstensi/Content-Type dari klien.
_SIGNATURES = ((b"\xff\xd8\xff", ".jpg"), (b"\x89PNG\r\n\x1a\n", ".png"))
_TYPES = {".jpg": "image/jpeg", ".png": "image/png"}


@lru_cache
def _client():
    s = get_settings()
    return boto3.client(
        "s3", endpoint_url=s.AWS_ENDPOINT_URL_S3,
        aws_access_key_id=s.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=s.AWS_SECRET_ACCESS_KEY,
        region_name=s.AWS_REGION,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"},
                      request_checksum_calculation="when_required",
                      response_checksum_validation="when_required"),
    )


def presign_proof_url(name: str) -> str:
    s = get_settings()
    return _client().generate_presigned_url(
        "get_object", Params={"Bucket": s.S3_BUCKET, "Key": f"proofs/{name}"},
        ExpiresIn=s.PRESIGN_EXPIRES_SECONDS)


async def save_proof_image(file: UploadFile) -> str:
    s = get_settings()
    data = await file.read(s.MAX_UPLOAD_BYTES + 1)
    if len(data) > s.MAX_UPLOAD_BYTES:
        raise ValidationFailed("Ukuran file maksimal 5 MB.")
    ext = next((e for sig, e in _SIGNATURES if data.startswith(sig)), None)
    if ext is None:
        raise ValidationFailed("Hanya file JPG atau PNG yang diperbolehkan.")

    name = f"{uuid4().hex}{ext}"  # nama dibuat server, nama asli klien diabaikan
    if s.STORAGE_BACKEND == "s3":
        try:
            await asyncio.to_thread(_client().put_object, Bucket=s.S3_BUCKET,
                                    Key=f"proofs/{name}", Body=data, ContentType=_TYPES[ext])
        except (BotoCoreError, ClientError) as exc:
            logger.exception("Upload ke storage gagal")
            raise AppException("Penyimpanan file bermasalah.", code="STORAGE_ERROR",
                            status_code=502) from exc
        return f"{s.UPLOAD_URL_PREFIX}/proofs/{name}"

    # STORAGE_BACKEND == "local": simpan ke disk (dev / fallback)
    folder = Path(s.UPLOAD_DIR) / "proofs"
    folder.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread((folder / name).write_bytes, data)
    return f"{s.UPLOAD_URL_PREFIX}/proofs/{name}"
