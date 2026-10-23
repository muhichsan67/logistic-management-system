# ALUR Logistik - Backend

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                   # isi DATABASE_URL & JWT_SECRET_KEY
psql -d alur_logistik -f ../database-logistic.sql      # skema utama
psql -d alur_logistik -f migrations/001_add_refresh_tokens.sql
uvicorn app.main:app --reload
pytest
```
Swagger: http://localhost:8000/docs  (klik **Authorize**, tempel `access_token`).
