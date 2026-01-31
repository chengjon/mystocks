"""
Base Schema Definitions

Provides reusable Pydantic base models with automatic data format validation.
All API schemas should inherit from these base classes to ensure consistency.

Reference: docs/api/API_SPECIFICATION.md
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, constr, validator

try:
    from app.core.data_formats import (
        DateFormat,
        StockSymbolFormat,
        get_current_iso_timestamp,
        get_current_ms_timestamp,
        validate_currency,
        validate_percentage,
        validate_price,
        validate_volume,
    )
except (ImportError, ModuleNotFoundError):
    # Fallback for script execution
    import os
    import sys

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from app.core.data_formats import (
        DateFormat,
        StockSymbolFormat,
        get_current_iso_timestamp,
        get_current_ms_timestamp,
        validate_currency,
        validate_percentage,
        validate_price,
        validate_volume,
    )


# ============================================================================
# STANDARD RESPONSE SCHEMAS
# ============================================================================


class StandardResponse(BaseModel):
    """Base response schema for all API responses"""

    status: str = Field(..., description="Response status: 'success' or 'error'")
    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    timestamp: str = Field(
        default_factory=get_current_iso_timestamp,
        description="ISO 8601 timestamp when response was generated",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "message": "Operation successful",
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


class SuccessResponse(StandardResponse):
    """Standard success response with data"""

    status: str = Field(default="success")
    data: Optional[Any] = Field(None, description="Response data payload")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "message": "Data retrieved successfully",
                "data": {"symbol": "600000", "price": 150.50},
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


class ErrorResponse(StandardResponse):
    """Standard error response"""

    status: str = Field(default="error")
    error: Optional[str] = Field(None, description="Error type/code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 400,
                "message": "Invalid request parameters",
                "error": "INVALID_PARAMETERS",
                "details": {"field": "symbol", "reason": "Invalid stock symbol format"},
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


class PaginationInfo(BaseModel):
    """Pagination metadata"""

    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: Optional[int] = Field(None, ge=0, description="Total number of pages")

    @validator("pages", pre=True, always=True)
    def calculate_pages(cls, v, values):
        if "total" in values and "page_size" in values:
            return (values["total"] + values["page_size"] - 1) // values["page_size"]
        return v if v is not None else 0

    class Config:
        json_schema_extra = {"example": {"page": 1, "page_size": 20, "total": 100, "pages": 5}}


class PaginatedResponse(StandardResponse):
    """Standard paginated response"""

    status: str = Field(default="success")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data with items and pagination info")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "message": "Data retrieved successfully",
                "data": {
                    "items": [
                        {"symbol": "600000", "price": 150.50},
                        {"symbol": "600001", "price": 45.25},
                    ],
                    "pagination": {
                        "page": 1,
                        "page_size": 20,
                        "total": 100,
                        "pages": 5,
                    },
                },
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error response (400)"""

    code: int = Field(default=400)
    error: str = Field(default="VALIDATION_ERROR")
    details: Dict[str, List[str]] = Field(..., description="Field-level validation errors")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 400,
                "message": "Validation failed",
                "error": "VALIDATION_ERROR",
                "details": {
                    "symbol": ["Invalid stock symbol format"],
                    "price": ["Price must be positive"],
                },
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


class UnauthorizedResponse(ErrorResponse):
    """Unauthorized error response (401)"""

    code: int = Field(default=401)
    error: str = Field(default="UNAUTHORIZED")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 401,
                "message": "Authentication required",
                "error": "UNAUTHORIZED",
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


class ForbiddenResponse(ErrorResponse):
    """Forbidden error response (403)"""

    code: int = Field(default=403)
    error: str = Field(default="FORBIDDEN")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 403,
                "message": "Permission denied",
                "error": "FORBIDDEN",
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


class NotFoundResponse(ErrorResponse):
    """Not found error response (404)"""

    code: int = Field(default=404)
    error: str = Field(default="NOT_FOUND")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 404,
                "message": "Resource not found",
                "error": "NOT_FOUND",
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


class ServerErrorResponse(ErrorResponse):
    """Server error response (500)"""

    code: int = Field(default=500)
    error: str = Field(default="INTERNAL_SERVER_ERROR")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 500,
                "message": "Internal server error",
                "error": "INTERNAL_SERVER_ERROR",
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


# ============================================================================
# STANDARD FIELD SCHEMAS
# ============================================================================


class StockSymbolField(BaseModel):
    """Stock symbol field (6-digit code)"""

    symbol: constr(min_length=6, max_length=6) = Field(
        ...,
        pattern=r"^\d{6}$",
        description="Stock symbol code (6 digits, e.g., '600000')",
    )

    @validator("symbol")
    def validate_symbol(cls, v):
        return StockSymbolFormat.validate(v)

    class Config:
        json_schema_extra = {"example": {"symbol": "600000"}}


class PriceField(BaseModel):
    """Price field with automatic precision handling"""

    price: Decimal = Field(..., ge=0, decimal_places=2, description="Price with 2 decimal places")

    @validator("price", pre=True)
    def validate_price_value(cls, v):
        return validate_price(v)

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}
        json_schema_extra = {"example": {"price": 150.50}}


class PercentageField(BaseModel):
    """Percentage field with automatic precision handling"""

    percentage: Decimal = Field(..., ge=-100, le=100, description="Percentage value (2-4 decimal places)")

    @validator("percentage", pre=True)
    def validate_percentage_value(cls, v):
        return validate_percentage(v)

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}
        json_schema_extra = {"example": {"percentage": 15.25}}


class VolumeField(BaseModel):
    """Trading volume field"""

    volume: int = Field(..., ge=0, description="Trading volume (integer)")

    @validator("volume", pre=True)
    def validate_volume_value(cls, v):
        return validate_volume(v)

    class Config:
        json_schema_extra = {"example": {"volume": 1000000}}


class CurrencyField(BaseModel):
    """Currency amount field with automatic precision handling"""

    amount: Decimal = Field(..., decimal_places=2, description="Currency amount with 2 decimal places")

    @validator("amount", pre=True)
    def validate_currency_value(cls, v):
        return validate_currency(v)

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}
        json_schema_extra = {"example": {"amount": 123456789.50}}


class DateField(BaseModel):
    """Date field (YYYY-MM-DD format)"""

    date: constr(pattern=r"^\d{4}-\d{2}-\d{2}$") = Field(..., description="Date in YYYY-MM-DD format")

    @validator("date", pre=True)
    def validate_date_value(cls, v):
        return DateFormat.validate(v)

    class Config:
        json_schema_extra = {"example": {"date": "2025-11-11"}}


class TimestampField(BaseModel):
    """Timestamp field (ISO 8601 format for REST)"""

    timestamp: str = Field(
        default_factory=get_current_iso_timestamp,
        description="ISO 8601 timestamp in UTC",
    )

    class Config:
        json_schema_extra = {"example": {"timestamp": "2025-11-11T12:34:56.789Z"}}


class MillisecondTimestampField(BaseModel):
    """Millisecond timestamp field (for WebSocket)"""

    timestamp: int = Field(
        default_factory=get_current_ms_timestamp,
        description="UTC millisecond timestamp",
    )

    class Config:
        json_schema_extra = {"example": {"timestamp": 1699267200000}}


# ============================================================================
# PAGINATION REQUEST/RESPONSE SCHEMAS
# ============================================================================


class PaginationRequest(BaseModel):
    """Standard pagination request parameters"""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")

    class Config:
        json_schema_extra = {"example": {"page": 1, "page_size": 20}}


class SortRequest(BaseModel):
    """Standard sorting request parameters"""

    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Sort order: 'asc' or 'desc'")

    class Config:
        json_schema_extra = {"example": {"sort_by": "price", "sort_order": "desc"}}


class FilterRequest(BaseModel):
    """Standard filter request parameters"""

    filters: Optional[Dict[str, Any]] = Field(None, description="Filter conditions as key-value pairs")

    class Config:
        json_schema_extra = {"example": {"filters": {"symbol": "600000", "price_min": 100, "price_max": 200}}}


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================


class AuthTokenResponse(StandardResponse):
    """Authentication token response"""

    status: str = Field(default="success")
    data: Dict[str, Any] = Field(..., description="Token information")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "message": "Authentication successful",
                "data": {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "refresh_token": "refresh_token_here",
                },
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


class CSRFTokenResponse(StandardResponse):
    """CSRF token response"""

    status: str = Field(default="success")
    data: Dict[str, str] = Field(..., description="CSRF token")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "message": "CSRF token generated",
                "data": {"csrf_token": "550e8400-e29b-41d4-a716-446655440000"},
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


# ============================================================================
# BATCH OPERATION SCHEMAS
# ============================================================================


class BatchOperation(BaseModel):
    """Single batch operation"""

    operation: str = Field(..., description="Operation type")
    data: Dict[str, Any] = Field(..., description="Operation data")
    id: Optional[str] = Field(None, description="Optional operation ID")

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "create",
                "data": {"symbol": "600000", "price": 150.50},
                "id": "op_1",
            }
        }


class BatchOperationRequest(BaseModel):
    """Batch operation request"""

    operations: List[BatchOperation] = Field(
        ..., min_items=1, max_items=100, description="List of operations to perform"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "operations": [
                    {
                        "operation": "create",
                        "data": {"symbol": "600000", "price": 150.50},
                        "id": "op_1",
                    },
                    {
                        "operation": "update",
                        "data": {"symbol": "600001", "price": 45.25},
                        "id": "op_2",
                    },
                ]
            }
        }


class BatchOperationResult(BaseModel):
    """Single batch operation result"""

    id: Optional[str] = Field(None, description="Operation ID")
    success: bool = Field(..., description="Whether operation succeeded")
    data: Optional[Any] = Field(None, description="Result data")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "op_1",
                "success": True,
                "data": {"id": 123},
                "error": None,
            }
        }


class BatchOperationResponse(StandardResponse):
    """Batch operation response"""

    status: str = Field(default="success")
    data: Dict[str, Any] = Field(..., description="Batch operation results")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "message": "Batch operations completed",
                "data": {
                    "results": [
                        {"id": "op_1", "success": True, "data": {"id": 123}},
                        {"id": "op_2", "success": False, "error": "Duplicate entry"},
                    ],
                    "summary": {"total": 2, "succeeded": 1, "failed": 1},
                },
                "timestamp": "2025-11-11T12:34:56.789Z",
            }
        }


if __name__ == "__main__":
    print("Base Schema Definitions Module")
    print("=" * 50)

    # Example: Create a success response
    response = SuccessResponse(status="success", code=200, message="Test successful", data={"test": "data"})
    print(f"\nSuccess Response:\n{response.json(indent=2)}")

    # Example: Create a paginated response
    pagination = PaginationInfo(page=1, page_size=20, total=100)
    print(f"\nPagination Info:\n{pagination.json(indent=2)}")

    print("\n✅ Base schema definitions module initialized successfully")
