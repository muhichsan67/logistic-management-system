import os

# Harus di-set SEBELUM modul app di-import.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-test-secret-test-secret-123")
os.environ.setdefault("BCRYPT_ROUNDS", "4")
