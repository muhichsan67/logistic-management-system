import os
import uuid
import magic
from fastapi import UploadFile, HTTPException, status

MAX_FILE_SIZE = 5 * 1024 * 1024  # Maksimal 5 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
UPLOAD_DIR = "static/proofs"

async def save_proof_image(file: UploadFile) -> str:
    contents = await file.read()
    
    # Validasi ukuran maksimal 5 MB
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "Ukuran file melebihi batas maksimal 5 MB", "code": "VALIDATION_ERROR"}
        )

    # Validasi tipe berdasarkan isi file (magic bytes), bukan hanya ekstensi
    mime_type = magic.from_buffer(contents, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "Format file tidak valid. Hanya JPG dan PNG yang diperbolehkan.", "code": "VALIDATION_ERROR"}
        )

    # Nama file di-generate server, dilarang memakai nama asli dari klien
    ext = ".jpg" if mime_type == "image/jpeg" else ".png"
    unique_filename = f"proof_{uuid.uuid4().hex}{ext}"
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    return f"/static/proofs/{unique_filename}"