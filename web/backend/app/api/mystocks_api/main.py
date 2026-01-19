from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import structlog

# Import existing core components
from app.core.error_codes import ErrorCode
from app.core.exception_handler import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,  # Import the config to apply production/dev settings
)

# Initialize logger
logger = structlog.get_logger(__name__)

# Configure exception handler (production vs development)
# For this new API, we will use the existing config from app.core.exception_handler
# Set ENVIRONMENT variable to "production" or "development"
os.environ["ENVIRONMENT"] = "development"  # For demonstration purposes, assume development

app = FastAPI(
    title="MyStocks Quant Algorithms API",
    description="提供 MyStocks 平台量化交易算法的 RESTful API 接口，支持外部调用和集成。",
    version="1.0.0",
)

# Register custom exception handlers using the existing handlers from app.core
# This ensures consistency with the project's API contract
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(
    ValidationError, validation_exception_handler
)  # Pydantic ValidationError not caught by RequestValidationError
app.add_exception_handler(SQLAlchemyError, database_exception_handler)

# --- Placeholder for Middleware (e.g., CORS, Rate Limiting) ---
# Will be added later if necessary based on overall project middleware setup

# --- Placeholder for Router Inclusion ---
# from routers import classification, management # Example imports
# app.include_router(classification.router, prefix="/api/v1")
# app.include_router(management.router, prefix="/api/v1")


@app.get("/api/v1/health", summary="Health check endpoint", tags=["System"])
async def health_check():
    """
    Checks the health of the API service.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "code": ErrorCode.SUCCESS.value,
            "message": "API service is healthy",
            "data": None,
            "request_id": getattr(app.state, "request_id", "unknown"),  # request_id will be set by a middleware
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# --- Request ID Middleware (Example) ---
# In a real project, a middleware would be responsible for setting request_id
# For now, let's add a simple one here to ensure request_id is always present
from uuid import uuid4
from datetime import datetime, timezone


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request.state.request_id = str(uuid4())
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Process-Time"] = str(process_time)
    return response


import time
