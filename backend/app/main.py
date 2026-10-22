from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.errors import error_payload, normalize_http_error

# Routers
from routers import admin, auth, shipment

app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content=normalize_http_error(exc.detail, exc.status_code),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_payload(
            "Request validation failed",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "VALIDATION_ERROR",
        ),
    )

api_v1 = APIRouter(prefix="/api/v1")

api_v1.include_router(auth.router)
api_v1.include_router(shipment.router)
api_v1.include_router(admin.router)

app.include_router(api_v1)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
