# Logistic Management System Backend

FastAPI backend for shipment creation, tracking, customer confirmation, courier
management, and administrative shipment operations.

## Folder structure

```text
backend/
├── app/
│   ├── main.py                 # FastAPI application and router registration
│   ├── core/
│   │   ├── config.py           # Environment-based application settings
│   │   ├── deps.py             # Database, JWT, and role dependencies
│   │   ├── errors.py           # Reusable API error helpers
│   │   └── security.py         # Password hashing and JWT creation
│   ├── db/
│   │   ├── session.py          # Async SQLAlchemy engine and sessions
│   │   └── models/             # SQLAlchemy database models
│   ├── routers/                # HTTP route handlers
│   ├── schemas/                # Pydantic request and response schemas
│   ├── services/               # Business logic and database operations
│   ├── jobs/                   # Scheduled/background jobs
│   └── tests/                  # Pytest test suite
├── .env                        # Local environment values (not committed)
├── .env.example                # Environment variable template
├── pyproject.toml              # UV project and dependency configuration
└── uv.lock                     # Locked dependency versions
```

The API is mounted under the `/api/v1` prefix.

## Environment configuration

Copy the template to `.env` and fill in the values:

```bash
cp .env.example .env
```

On PowerShell:

```powershell
Copy-Item .env.example .env
```

Example:

```env
DATABASE_URL=neondb_owner:password@host/database?sslmode=require
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
```

| Variable | Required | Description |
|---|---:|---|
| `DATABASE_URL` | Yes | PostgreSQL connection details. The application adds the `postgresql+psycopg://` driver prefix when creating the async SQLAlchemy engine. |
| `SECRET_KEY` | Yes | Secret used to sign and verify JWT access tokens. Keep it private and use a strong random value. |
| `ALGORITHM` | No | JWT signing algorithm. Defaults to `HS256`. |
| `ACCESS_TOKEN_EXPIRE_HOURS` | No | JWT lifetime in hours. Defaults to `24`. |

Do not commit `.env` or database credentials to source control.

## Modules and endpoints

All endpoints below are prefixed with `/api/v1`.

### Authentication

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/auth/register` | Public | Register a customer account. |
| `POST` | `/auth/login` | Public | Authenticate and receive a JWT bearer token. |

### Customer shipments

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/shipments` | `CUSTOMER` | Create a shipment in `PENDING` status and create its initial tracking history. |
| `GET` | `/shipments/me` | `CUSTOMER` | List the current customer's shipments. Supports `status`, `page`, and `limit`. |
| `PUT` | `/shipments/{id}/confirm` | `CUSTOMER` | Confirm a delivered shipment and change it to `COMPLETED`. |
| `GET` | `/shipments/{id}/detail` | `ADMIN`, assigned `COURIER` | View shipment detail, customer, courier, and tracking history. |
| `GET` | `/shipments/{tracking_number}/track` | Public | Track a shipment by tracking number. |

### Admin dashboard and settings

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/admin/dashboard/summary` | `ADMIN` | Return shipment counters for pending, in-transit, delivered today, and rejected shipments. |
| `PUT` | `/admin/settings` | `ADMIN` | Save `pending_alert_timeout_minutes` and `auto_complete_days`. |
| `GET` | `/admin/shipments` | `ADMIN` | List all shipments with filters and pagination. |

Supported `/admin/shipments` query parameters:

- `status`
- `courier_id`
- `date_from`
- `date_to`
- `q` for tracking-number search
- `page`
- `limit`

Pending shipments are ordered first, followed by newest shipments. Each item
contains `is_overdue_pending`.

### Admin courier management

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/admin/couriers` | `ADMIN` | Create a courier account. |
| `GET` | `/admin/couriers` | `ADMIN` | List couriers with pagination. |
| `GET` | `/admin/couriers/options` | `ADMIN` | List active couriers with only `id` and `name`. |
| `PUT` | `/admin/couriers/{courier_id}` | `ADMIN` | Update courier information. |
| `DELETE` | `/admin/couriers/{courier_id}` | `ADMIN` | Soft-delete a courier by setting `is_active` to `false`. |

### Admin shipment actions

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `PUT` | `/admin/shipments/{shipment_id}/assign` | `ADMIN` | Assign an active courier to a pending shipment. |
| `PUT` | `/admin/shipments/{shipment_id}/reject` | `ADMIN` | Reject a pending shipment with a reason. |

Status-changing operations create an append-only tracking-history record in the
same database transaction as the shipment update.

## Authentication

Protected endpoints use the bearer token returned by `/auth/login`:

```http
Authorization: Bearer <access_token>
```

Role restrictions are enforced by the backend. A customer, courier, or admin
cannot use endpoints assigned to another role.

## Error format

All API errors use this JSON shape:

```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

Common status codes:

| HTTP status | Meaning | Example code |
|---:|---|---|
| `400` | Invalid request or business input | `VALIDATION_ERROR` |
| `401` | Missing, invalid, or expired token | `UNAUTHORIZED` |
| `403` | Insufficient role or resource ownership | `FORBIDDEN` |
| `404` | Resource or route not found | `NOT_FOUND` |
| `409` | Invalid state transition or duplicate data | `INVALID_STATUS_TRANSITION`, `DUPLICATE` |
| `422` | Request schema validation failure | `VALIDATION_ERROR` |
| `500` | Unexpected server-side failure | `INTERNAL_ERROR` |

Validation and HTTP exception handlers in `app/main.py` normalize framework
errors so they do not produce nested `detail` objects.

## Install and run with UV

From the `backend` directory, synchronize the project dependencies:

```bash
uv sync
```

The development dependency group includes `pytest`.

The application currently imports `core`, `routers`, `services`, and other
directories as top-level modules. Set `PYTHONPATH` to `app` before running it.

Linux/macOS/WSL:

```bash
export PYTHONPATH="$PWD/app"
uv run fastapi dev app/main.py
```

PowerShell:

```powershell
$env:PYTHONPATH = "$PWD\app"
uv run fastapi dev app\main.py
```

The development server is normally available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Run tests with Pytest

Set the same import path from the `backend` directory:

Linux/macOS/WSL:

```bash
export PYTHONPATH="$PWD/app"
uv run pytest app/tests -v
```

PowerShell:

```powershell
$env:PYTHONPATH = "$PWD\app"
uv run pytest app\tests -v
```

Run one test module:

```bash
uv run pytest app/tests/test_auth.py -v
uv run pytest app/tests/test_customer.py -v
uv run pytest app/tests/test_admin.py -v
```

Run one test:

```bash
uv run pytest app/tests/test_customer.py::test_confirm_shipment_service_changes_delivered_to_completed -v
```

The current tests use mocked async database sessions for service and router
coverage, so a running PostgreSQL instance is not required for the test suite.