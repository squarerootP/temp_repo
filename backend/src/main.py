import json
import logging
import time
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.src.infrastructure.config.settings import settings
from backend.src.infrastructure.persistence.database import create_tables
from backend.src.presentation.routers.v1 import books, rag, users
from backend.src.presentation.routers.v1.api import router as api_router

RATE_LIMIT = settings.RATE_LIMIT
WINDOW_SIZE = settings.RATE_LIMIT_WINDOW_SIZE

request_counts = {}
app = FastAPI()


@app.on_event("startup")
def startup_event():
    create_tables()


### LOGGING
# logger for all logs
all_logger = logging.getLogger("all_logs")
all_logger.setLevel(logging.INFO)

all_handler = RotatingFileHandler(
    r"logs\app.log", maxBytes=5 * 1024 * 1024, backupCount=5
)
all_logger.addHandler(all_handler)
# Logger for validation errors:
val_logger = logging.getLogger("val_err")
val_logger.setLevel(logging.ERROR)
val_handler = RotatingFileHandler(
    r"logs\val_err.log", maxBytes=5 * 1024 * 1024, backupCount=5
)
val_logger.addHandler(val_handler)

# Logger for general exceptions
exc_logger = logging.getLogger("exc_err")
exc_logger.setLevel(logging.ERROR)
exc_handler = RotatingFileHandler(
    r"logs\exc_err.log", maxBytes=5 * 1024 * 1024, backupCount=5
)
exc_logger.addHandler(exc_handler)


### MIDDLEWARES
@app.middleware("http")
async def log_requests(request: Request, call_next):
    all_logger.info(f"Incoming request: {request.method} {request.url}")

    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    all_logger.info(
        f"Completed request: {request.method} {request.url}"
        f"Status: {response.status_code} "
        f"Duration: {process_time:.2f}ms"
    )
    return response


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host  # type: ignore
    now = time.time()

    timestamps = request_counts.get(client_ip, [])
    timestamps = [ts for ts in timestamps if now - ts < WINDOW_SIZE]
    if len(timestamps) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429, content={"detail": "Rate limit exceeded. Try again later."}
        )
    timestamps.append(now)
    request_counts[client_ip] = timestamps
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    error_data = {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": str(request.url),
        "method": request.method,
    }
    all_logger.error(json.dumps(error_data))
    exc_logger.error(json.dumps(error_data))

    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    error_data = {
        "error": "Validation error",
        "details": exc.errors(),
        "body": body.decode() if body else "",
        "path": str(request.url),
        "method": request.method,
    }
    all_logger.error(json.dumps(error_data))
    val_logger.error(json.dumps(error_data))
    return JSONResponse(status_code=422, content=error_data)


### CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://localhost:5173",        # <-- Vite frontend
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### ROUTERS
app.include_router(api_router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(books.router, prefix="/v1")
app.include_router(rag.router, prefix="/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Library Management System API"}
